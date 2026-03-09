"""速率限制配置。"""

from slowapi import Limiter
from slowapi.util import get_remote_address

# 创建速率限制器实例
limiter = Limiter(key="workmatch-rate-limiter")

# 速率限制配置
RATE_LIMITS = {
    "default": "100/minute",
    "auth": "5/minute",  # 登录接口更严格
    "create": "20/minute",  # 创建资源更严格
    "update": "30/minute",  # 更新资源更宽松
    "delete": "10/minute",  # 删除资源最严格
}


def get_rate_limit(limit_name: str = "default") -> tuple[int, int]:
    """获取速率限制配置。"""
    limits = RATE_LIMITS.get(limit_name, RATE_LIMITS["default"])
    return limits
