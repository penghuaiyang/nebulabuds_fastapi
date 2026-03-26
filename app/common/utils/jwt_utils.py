from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from app.core.config import settings
from functools import wraps
from typing import Callable
import asyncio
import inspect
from fastapi import Request
from app.common.exception.exceptions import AuthenticationException


class JWTManager:

    def __init__(self):
        self.secret_key = settings.jwt_secret_key
        self.algorithm = settings.jwt_algorithm
        self.access_token_expire_minutes = settings.access_expires_minutes
        self.refresh_token_expire_days = settings.refresh_expires_days  # 30天

    def create_access_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """创建访问令牌"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)

        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "access"
        })

        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt

    def create_refresh_token(self, data: Dict[str, Any]) -> str:
        """创建刷新令牌"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=self.refresh_token_expire_days)
        now = datetime.utcnow()

        to_encode.update({
            "exp": expire,
            "iat": now,
            "type": "refresh"
        })

        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt

    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm],
                options={"verify_exp": True, "verify_iat": True}
            )
            return payload
        except JWTError:
            return None

    def refresh_tokens(self, request: Request) -> Dict[str, str]:
        auth_header: str = request.headers.get("Authorization", "")
        parts = auth_header.split()
        print(len(parts))
        print(parts[0])
        if len(parts) != 2 or parts[0] != "Bearer":
            raise AuthenticationException(message="无效的认证令牌格式")
        refresh_token = parts[1]
        payload = self.verify_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            raise AuthenticationException(message="无效的刷新令牌")
        user_data = {k: v for k, v in payload.items() if k not in {"exp", "iat", "type"}}
        new_access_token = self.create_access_token(user_data)
        new_refresh_token = self.create_refresh_token(user_data)
        return {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token
        }


def no_auth_required(func: Callable) -> Callable:
    if asyncio.iscoroutinefunction(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            return await func(*args, **kwargs)

        async_wrapper._no_auth_required = True
        return async_wrapper
    else:
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        sync_wrapper._no_auth_required = True
        return sync_wrapper


def auth_required(func: Callable) -> Callable:
    if asyncio.iscoroutinefunction(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            return await func(*args, **kwargs)

        async_wrapper._auth_required = True
        return async_wrapper
    else:
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        sync_wrapper._auth_required = True
        return sync_wrapper


# 全局JWT管理器实例
jwt_manager = JWTManager()


class AdminJWTManager:

    def __init__(self):
        self.secret_key = settings.jwt_admin_secret_key
        self.algorithm = settings.jwt_admin_algorithm
        self.access_token_expire_minutes = settings.jwt_admin_access_expires_minutes
        self.refresh_token_expire_days = settings.jwt_admin_refresh_expires_days

    def create_access_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """创建 Admin 访问令牌"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)

        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "access"
        })

        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt

    def create_refresh_token(self, data: Dict[str, Any]) -> str:
        """创建 Admin 刷新令牌"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=self.refresh_token_expire_days)

        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "refresh"
        })

        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt

    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """验证 Admin Token"""
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm],
                options={"verify_exp": True, "verify_iat": True}
            )
            return payload
        except JWTError:
            return None

    def refresh_tokens(self, request: Request) -> Dict[str, str]:
        """刷新 Admin Token"""
        auth_header: str = request.headers.get("Authorization", "")
        parts = auth_header.split()
        if len(parts) != 2 or parts[0] != "Bearer":
            raise AuthenticationException(message="无效的认证令牌格式")
        refresh_token = parts[1]
        payload = self.verify_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            raise AuthenticationException(message="无效的刷新令牌")
        user_data = {k: v for k, v in payload.items() if k not in {"exp", "iat", "type"}}
        new_access_token = self.create_access_token(user_data)
        new_refresh_token = self.create_refresh_token(user_data)
        return {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token
        }


# 全局 Admin JWT 管理器实例
admin_jwt_manager = AdminJWTManager()
