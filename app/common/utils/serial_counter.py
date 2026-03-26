"""
Redis 序号计数器模块

用于批量导入时分配连续的序号，支持：
- 原子递增获取号段
- 初始化计数器
- 同步到数据库备份
"""

from typing import Tuple, Optional

from app.common.utils.log_utils import log_util
from app.db.redis import get_redis_client

logger = log_util.get_logger("serial_counter")

# 序号计数器键模板（区分不同业务）
SERIAL_NO_KEY_TEMPLATE = "active_code:serial_no:{product_type}"
MAC_SERIAL_NO_KEY_TEMPLATE = "mac_address:serial_no"

def _resolve_counter_key(key_template: str, product_type: Optional[int]) -> str:
    """生成 Redis 计数器 key，兼容按产品类型和全局两种模式。"""
    if "{product_type}" in key_template:
        if product_type is None:
            raise ValueError("当前计数器需要提供 product_type")
        return key_template.format(product_type=product_type)
    return key_template


def _get_counter_scope(product_type: Optional[int]) -> str:
    """返回计数器作用域描述。"""
    return f"product_type={product_type}" if product_type is not None else "global"


async def init_counter(
    product_type: Optional[int] = None,
    value: int = 0,
    key_template: str = SERIAL_NO_KEY_TEMPLATE,
) -> bool:
    """
    初始化序号计数器

    Args:
        product_type: 产品类型；当 key_template 不带 {product_type} 时可为空
        value: 初始值，默认为 0

    Returns:
        是否初始化成功
    """
    client = await get_redis_client()
    if client is None:
        logger.error("Redis client not available")
        return False

    key = _resolve_counter_key(key_template, product_type)
    # SETNX 只在键不存在时设置
    result = await client.setnx(key, value)
    if result:
        logger.info(f"Initialized counter for {_get_counter_scope(product_type)} with value={value}")
    return bool(result)


async def get_counter(product_type: Optional[int] = None, key_template: str = SERIAL_NO_KEY_TEMPLATE) -> int:
    """
    获取当前序号

    Args:
        product_type: 产品类型；当 key_template 不带 {product_type} 时可为空

    Returns:
        当前序号值，不存在返回 0
    """
    client = await get_redis_client()
    if client is None:
        logger.error("Redis client not available")
        return 0

    key = _resolve_counter_key(key_template, product_type)
    value = await client.get(key)
    return int(value) if value else 0


async def incrby(
    product_type: Optional[int] = None,
    increment: int = 0,
    key_template: str = SERIAL_NO_KEY_TEMPLATE,
) -> int:
    """
    原子递增获取号段起点

    Args:
        product_type: 产品类型；当 key_template 不带 {product_type} 时可为空
        increment: 递增量（即需要分配的序号数量）

    Returns:
        号段起点序号，失败返回 -1
    """
    client = await get_redis_client()
    if client is None:
        logger.error("Redis client not available")
        return -1

    key = _resolve_counter_key(key_template, product_type)

    # 确保计数器已初始化
    await client.setnx(key, 0)

    # 原子递增并返回操作前的值（即号段起点）
    start_no = await client.incrby(key, increment)

    logger.debug(f"Allocated serial no range for {_get_counter_scope(product_type)}: "
                 f"start={start_no - increment + 1}, end={start_no}, count={increment}")

    return start_no - increment + 1


async def allocate_range(
    product_type: Optional[int] = None,
    count: int = 0,
    key_template: str = SERIAL_NO_KEY_TEMPLATE,
) -> Tuple[int, int]:
    """
    分配一个连续的序号段

    Args:
        product_type: 产品类型；当 key_template 不带 {product_type} 时可为空
        count: 需要分配的序号数量

    Returns:
        (start_no, end_no) 序号段范围，失败返回 (-1, -1)
    """
    if count <= 0:
        logger.warning(f"Invalid count {count} for {_get_counter_scope(product_type)}")
        return -1, -1

    start_no = await incrby(product_type, count, key_template=key_template)
    if start_no < 0:
        logger.error(f"Failed to allocate range for {_get_counter_scope(product_type)}, count={count}")
        return -1, -1

    end_no = start_no + count - 1
    return start_no, end_no


async def set_counter(
    product_type: Optional[int] = None,
    value: int = 0,
    key_template: str = SERIAL_NO_KEY_TEMPLATE,
) -> bool:
    """
    手动设置序号值（用于修正或恢复）

    Args:
        product_type: 产品类型；当 key_template 不带 {product_type} 时可为空
        value: 要设置的值

    Returns:
        是否设置成功
    """
    client = await get_redis_client()
    if client is None:
        logger.error("Redis client not available")
        return False

    key = _resolve_counter_key(key_template, product_type)
    await client.set(key, value)
    logger.info(f"Set counter for {_get_counter_scope(product_type)} to value={value}")
    return True
