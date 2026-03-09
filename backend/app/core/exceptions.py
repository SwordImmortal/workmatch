"""自定义异常类。"""


class AppException(Exception):
    """应用基础异常。"""

    def __init__(self, message: str, code: str = "INTERNAL_ERROR"):
        self.message = message
        self.code = code
        super().__init__(message)


class NotFoundException(AppException):
    """资源未找到异常。"""

    def __init__(self, resource: str, resource_id: int | None = None):
        super().__init__(f"{resource} 不存在", "NOT_FOUND")


class ForbiddenException(AppException):
    """权限不足异常。"""

    def __init__(self, message: str = "无权访问此资源"):
        super().__init__(message, "FORBIDDEN")


class DuplicateException(AppException):
    """重复资源异常。"""

    def __init__(self, resource: str, field: str, value: str):
        super().__init__(f"{resource} 的 {field} 已存在: {value}", "DUPLICATE")


class ValidationException(AppException):
    """验证失败异常。"""

    def __init__(self, message: str):
        super().__init__(message, "VALIDATION_ERROR")


class RateLimitException(AppException):
    """速率限制异常。"""

    def __init__(self, retry_after: int | None = None):
        self.retry_after = retry_after
        super().__init__("请求过于频繁，请稍后重试", "RATE_LIMIT")
