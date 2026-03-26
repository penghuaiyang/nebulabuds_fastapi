from starlette.middleware.base import BaseHTTPMiddleware
from app.common import api_write


class HeaderMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        header = request.headers
        required_fields = ["X-Client-Lang", "X-Device-Brand", "X-Device-ID"]
        for field in required_fields:
            if field not in header:
                response = await api_write(
                    code=-28,
                    message=f"缺少请求头: {field}",
                    request=request
                )
                return response

        return await call_next(request)
