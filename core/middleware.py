import logging
import time

logger = logging.getLogger("api.requests")

class ForceCorsHeaderMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response["Access-Control-Allow-Origin"] = "*"
        return response


class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start = time.time()

        response = self.get_response(request)

        duration = time.time() - start

        logger.info(
            f"{request.method} {request.path} "
            f"user={request.user if request.user.is_authenticated else 'anon'} "
            f"status={response.status_code} "
            f"time={duration:.2f}s"
        )

        return response