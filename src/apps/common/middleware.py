"""
Common middleware for the application.
"""

import logging
import time

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware:
    """Log all HTTP requests with timing and status codes."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = time.time()

        response = self.get_response(request)

        duration = time.time() - start_time

        # Log the request
        logger.info(
            f"{request.method} {request.get_full_path()} {response.status_code} "
            f"[{duration:.3f}s, {self.get_client_ip(request)}]"
        )

        return response

    def get_client_ip(self, request):
        """Get the client IP address from the request."""
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]
        else:
            ip = request.META.get("REMOTE_ADDR")
        return ip
