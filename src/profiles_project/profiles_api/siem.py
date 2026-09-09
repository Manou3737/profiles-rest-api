import json
from datetime import timedelta
from pathlib import Path

from django.conf import settings
from django.utils import timezone

from .models import SecurityEvent


def get_client_ip(request):
    """Return the client's IP address from the request."""
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")

    if x_forwarded_for:
        return x_forwarded_for.split(",")[0].strip()

    return request.META.get("REMOTE_ADDR")


def _write_siem_log(
    security_event,
    details=None,
):
    """Write a SecurityEvent as a structured JSONL event."""

    logs_dir = Path(settings.BASE_DIR) / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)

    log_file = logs_dir / "security-events.jsonl"

    event_data = {
        "@timestamp": security_event.created_at.isoformat(),
        "event": {
            "action": security_event.event_type,
        },
        "source": {
            "ip": security_event.ip_address,
        },
        "url": {
            "path": security_event.request_path,
        },
        "user_agent": {
            "original": security_event.user_agent,
        },
    }

    if security_event.user_id is not None:
        event_data["user"] = {
            "id": security_event.user_id,
        }

    if details is not None:
        if isinstance(details, dict):
            event_data["message"] = json.dumps(details)
            event_data["event"]["details"] = details
        else:
            event_data["message"] = str(details)

    with log_file.open("a", encoding="utf-8") as file:
        file.write(
            json.dumps(
                event_data,
                ensure_ascii=False,
            )
            + "\n"
        )


def create_security_event(
    request,
    event_type,
    details=None,
    user=None,
):
    """Create a centralized SecurityEvent record and SIEM JSONL event."""

    if user is None and request is not None:
        if request.user.is_authenticated:
            user = request.user

    ip_address = get_client_ip(request) if request is not None else None

    path = request.path if request is not None else None

    user_agent = (
        request.META.get("HTTP_USER_AGENT", "")
        if request is not None
        else ""
    )

    original_details = details

    if isinstance(details, dict):
        details = json.dumps(details)

    security_event = SecurityEvent.objects.create(
        user=user,
        event_type=event_type,
        ip_address=ip_address,
        request_path=path,
        user_agent=user_agent,
        details=details or "",
    )

    _write_siem_log(
        security_event,
        details=original_details,
    )

    return security_event


def detect_brute_force(
    ip_address,
    threshold=5,
    window_minutes=5,
):
    """
    Detect multiple failed login attempts from the same IP
    within a defined time window.
    """

    if not ip_address:
        return False

    window_start = timezone.now() - timedelta(minutes=window_minutes)

    failed_attempts = SecurityEvent.objects.filter(
        event_type="LOGIN_FAILED",
        ip_address=ip_address,
        created_at__gte=window_start,
    ).count()

    if failed_attempts < threshold:
        return False

    detection_exists = SecurityEvent.objects.filter(
        event_type="BRUTE_FORCE_DETECTED",
        ip_address=ip_address,
        created_at__gte=window_start,
    ).exists()

    if not detection_exists:
        security_event = SecurityEvent.objects.create(
            event_type="BRUTE_FORCE_DETECTED",
            ip_address=ip_address,
            request_path="",
            user_agent="",
            details=(
                f"Brute-force attack detected. "
                f"{failed_attempts} failed login attempts "
                f"within {window_minutes} minutes."
            ),
        )

        _write_siem_log(
            security_event,
            details=security_event.details,
        )

    return True
