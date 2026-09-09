from datetime import timedelta

from django.utils import timezone
from django.conf import settings
from .models import SecurityEvent
from .siem import create_security_event, get_client_ip


BRUTE_FORCE_THRESHOLD = 5
BRUTE_FORCE_WINDOW_MINUTES = 5


def detect_brute_force(request):
    """Detect repeated failed login attempts from the same IP."""

    ip_address = get_client_ip(request)

    if not ip_address:
        return None

    window_start = (
        timezone.now()
        - timedelta(minutes=BRUTE_FORCE_WINDOW_MINUTES)
    )

    failed_attempts = SecurityEvent.objects.filter(
        event_type='LOGIN_FAILED',
        ip_address=ip_address,
        created_at__gte=window_start,
    ).count()

    if failed_attempts == BRUTE_FORCE_THRESHOLD:
        return create_security_event(
            request=request,
            event_type='BRUTE_FORCE_DETECTED',
            details=(
                f'Brute force detected: {failed_attempts} failed login '
                f'attempts from IP {ip_address} within '
                f'{BRUTE_FORCE_WINDOW_MINUTES} minutes.'
            ),
        )

    return None

def detect_suspicious_ip(request):
    """Detect requests originating from configured suspicious IP addresses."""

    ip_address = get_client_ip(request)

    if not ip_address:
        return None

    suspicious_ips = getattr(settings, 'SIEM_SUSPICIOUS_IPS', [])

    if ip_address not in suspicious_ips:
        return None

    return create_security_event(
        request=request,
        event_type='SUSPICIOUS_IP_DETECTED',
        details=(
            f'Suspicious IP detected: {ip_address}. '
            f'Request originated from a configured suspicious IP address.'
        ),
    )
