import logging
import time

from starlette.middleware.base import BaseHTTPMiddleware


logger = logging.getLogger(__name__)


class RequestLoggerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        
        # 1. Record the exact start time
        start = time.time()
    
        # 2. Send the request forward to its intended route (e.g., webhook, health check)
        response = await call_next(request)

        # 3. Calculate how long the request took to process
        duration = round(time.time() - start, 4)

        # 4. Log the details (Method, Path, Status Code, and Duration)
        logger.info(
            "%s %s %s %.4fs",
            request.method,
            request.url.path,
            response.status_code,
            duration,
        )
        
        # 5. Return the response back to the user/client
        return response