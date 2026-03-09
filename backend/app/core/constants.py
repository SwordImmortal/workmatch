"""全局常量定义。"""

# 分页限制
MAX_PAGE_SIZE = 100
DEFAULT_PAGE_SIZE = 20


def validate_pagination(skip: int = 0, limit: int = DEFAULT_PAGE_SIZE) -> tuple[int, int]:
    """验证分页参数。

    Args:
        skip: 跳过的记录数
        limit: 每页记录数

    Returns:
        验证后的 (skip, limit) 元组
    """
    if skip < 0:
        skip = 0
    if limit < 1:
        limit = DEFAULT_PAGE_SIZE
    if limit > MAX_PAGE_SIZE:
        limit = MAX_PAGE_SIZE
    return skip, limit

