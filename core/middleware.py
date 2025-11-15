import time
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
from django.utils.timezone import now

from accounts.models import AuditLog  # local import to avoid circular at startup


class RequestAuditMiddleware(MiddlewareMixin):
    """Logs each request to AuditLog model with duration and outcome.

    This middleware intentionally avoids printing and writes to DB.
    """

    def process_request(self, request):
        request._audit_start = time.time()

    def process_response(self, request, response):
        try:
            duration = time.time() - getattr(request, '_audit_start', time.time())
            user = getattr(request, 'user', None)
            AuditLog.objects.create(
                user=user if getattr(user, 'is_authenticated', False) else None,
                action=f"{request.method} {request.path}",
                timestamp=now(),
                metadata={'status_code': response.status_code, 'duration': duration},
            )
        except Exception:
            # Don't let logging break requests
            pass
        return response
