from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute
from starlette.middleware.base import BaseHTTPMiddleware
from typing import List, Optional

from app.common.utils.jwt_utils import jwt_manager
from app.common import log_util

logger = log_util.get_logger("jwt_middleware")


class JWTMiddleware(BaseHTTPMiddleware):
    """JWT认证中间件"""

    def __init__(self, app, exclude_paths: Optional[List[str]] = None):
        super().__init__(app)
        # 默认排除的路径（不需要认证）
        self.exclude_paths = exclude_paths or [
            "/docs",
            "/redoc",
            "/openapi.json",
            "/health"
        ]

    def _is_excluded_path(self, path: str) -> bool:
        """检查路径是否被排除"""
        for exclude_path in self.exclude_paths:
            # 支持通配符匹配
            if exclude_path.endswith("*"):
                if path.startswith(exclude_path[:-1]):
                    return True
            elif path == exclude_path or path.startswith(exclude_path + "/"):
                return True
        return False

    def _check_route_auth_requirement(self, request: Request) -> bool:
        """检查路由是否需要认证"""
        # 获取当前路由
        for route in request.app.routes:
            if hasattr(route, 'path_regex') and route.path_regex.match(request.url.path):
                if isinstance(route, APIRoute):
                    # 检查路由的endpoint函数是否有认证标记
                    endpoint = route.endpoint
                    if hasattr(endpoint, '_no_auth_required'):
                        return False  # 不需要认证
                    # 默认需要认证
                    return True
        return True  # 默认需要认证

    def _extract_token_from_header(self, authorization: str) -> Optional[str]:
        """从Authorization头中提取token"""
        if not authorization.startswith("Bearer "):
            return None

        parts = authorization.split(" ")
        if len(parts) != 2:
            return None

        return parts[1]

    def _create_auth_error_response(self, message: str) -> JSONResponse:
        """创建认证错误响应"""
        return JSONResponse(
            status_code=200,
            content={
                "code": -21,
                "message": "认证失败",
                "data": {
                    "detail": message
                }
            }
        )

    async def dispatch(self, request: Request, call_next):
        """中间件处理逻辑"""
        path = request.url.path
        method = request.method
        client_ip = request.client.host if request.client else "unknown"

        # 检查是否为排除路径
        if self._is_excluded_path(path):
            logger.debug(f"跳过JWT验证（排除路径） | 路径: {path} | 方法: {method}")
            return await call_next(request)

        # 检查路由是否需要认证
        if not self._check_route_auth_requirement(request):
            logger.debug(f"跳过JWT验证（装饰器标记） | 路径: {path} | 方法: {method}")
            return await call_next(request)

        # 获取Authorization头
        authorization: str = request.headers.get("Authorization", "")

        if not authorization:
            logger.warning(f"缺少Authorization头 | 路径: {path} | 方法: {method} | IP: {client_ip}")
            return self._create_auth_error_response("缺少认证令牌")

        # 提取token
        token = self._extract_token_from_header(authorization)
        if not token:
            logger.warning(f"无效的Authorization格式 | 路径: {path} | 方法: {method} | IP: {client_ip}")
            return self._create_auth_error_response("无效的认证令牌格式")

        # 验证token
        payload = jwt_manager.verify_token(token)
        if not payload:
            logger.warning(f"JWT令牌验证失败 | 路径: {path} | 方法: {method} | IP: {client_ip}")
            return self._create_auth_error_response("无效或已过期的认证令牌")

        # 检查token类型
        token_type = payload.get("type")
        if token_type != "access":
            logger.warning(f"错误的令牌类型: {token_type} | 路径: {path} | 方法: {method} | IP: {client_ip}")
            return self._create_auth_error_response("无效的令牌类型")

        # 验证必要字段
        user_id = payload.get("userid")
        if not user_id:
            logger.warning(f"令牌缺少用户ID | 路径: {path} | 方法: {method} | IP: {client_ip}")
            return self._create_auth_error_response("无效的用户令牌")

        # 将用户信息添加到request state中
        request.state.user_id = user_id
        request.state.user_pk = payload.get("user_pk")
        request.state.username = payload.get("username")
        request.state.user_role = payload.get("role")
        request.state.user_payload = payload
        request.state.token = token

        logger.info(
            f"JWT认证成功 | 用户ID: {user_id} | 用户名: {payload.get('username')} | 路径: {path} | 方法: {method}")

        return await call_next(request)
