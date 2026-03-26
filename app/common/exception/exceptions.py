from typing import Any, Dict, Optional


class BaseAPIException(Exception):
    """基础API异常类"""

    def __init__(
            self,
            message: str = "服务器内部错误",
            code: int = -1,
            message_language: str = "cn",
            details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.code = code
        self.message_language = message_language
        self.details = details or {}
        super().__init__(self.message)


class ValidationException(BaseAPIException):
    """参数验证异常"""

    def __init__(self, message: str = "参数验证失败", details: Optional[Dict[str, Any]] = None):
        super().__init__(message=message, code=-24, details=details)


class AuthenticationException(BaseAPIException):
    """认证异常"""

    def __init__(self, message: str = "认证失败", details: Optional[Dict[str, Any]] = None):
        super().__init__(message=message, code=-21, details=details)


class AuthorizationException(BaseAPIException):
    """授权异常"""

    def __init__(self, message: str = "权限不足", details: Optional[Dict[str, Any]] = None):
        super().__init__(message=message, code=-22, details=details)


class NotFoundException(BaseAPIException):
    """资源不存在异常"""

    def __init__(self, message: str = "资源不存在", details: Optional[Dict[str, Any]] = None):
        super().__init__(message=message, code=-23, details=details)


class BusinessException(BaseAPIException):
    """业务逻辑异常"""

    def __init__(self, message: str = "业务处理失败", details: Optional[Dict[str, Any]] = None):
        super().__init__(message=message, code=-25, details=details)


class DatabaseException(BaseAPIException):
    """数据库异常"""

    def __init__(self, message: str = "数据库操作失败", details: Optional[Dict[str, Any]] = None):
        super().__init__(message=message, code=-26, details=details)


class ExternalServiceException(BaseAPIException):
    """外部服务异常"""

    def __init__(self, message: str = "外部服务调用失败", details: Optional[Dict[str, Any]] = None):
        super().__init__(message=message, code=-27, details=details)


class HeaderException(BaseAPIException):
    """请求头验证异常"""

    def __init__(self, message: str = "请求头验证失败", details: Optional[Dict[str, Any]] = None):
        super().__init__(message=message, code=-28, details=details)
