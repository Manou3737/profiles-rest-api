from rest_framework.views import exception_handler

from . import models
from .siem import create_security_event


def audit_exception_handler(exc, context):
    """Log authenticated unauthorized access attempts."""

    response = exception_handler(exc, context)

    if response is not None and response.status_code == 403:
        request = context.get('request')
        user = getattr(request, 'user', None)

        if user is not None and user.is_authenticated:
            endpoint = request.path
            details = (
                f'Unauthorized access attempt to {endpoint}.'
            )

            models.AuditLog.objects.create(
                user=user,
                action='UNAUTHORIZED_ACCESS',
                details=details,
            )

            create_security_event(
                request=request,
                user=user,
                event_type='UNAUTHORIZED_ACCESS',
                details=details,
            )

    return response
