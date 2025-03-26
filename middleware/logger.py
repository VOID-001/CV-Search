from starlette.requests import Request
from starlette.responses import Response

async def log_requests(request: Request, call_next):
    response = await call_next(request)
    # Implement logging logic here: Log the request path, method, and response status.
    return response