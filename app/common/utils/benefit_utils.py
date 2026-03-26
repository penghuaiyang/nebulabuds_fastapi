"""权益工具方法"""

from datetime import timedelta

from tortoise import timezone

from app.db.redis import get_redis_client
from app.db.redis_keys import RedisKeys
from app.models.models import Benefit, BenefitDeductionLog, MacAddressBinding

DEDUCT_BENEFIT_DURATION_LUA = """
local current = redis.call("GET", KEYS[1])
if not current then
    return {-1, -1}
end
current = tonumber(current)
local deduct = tonumber(ARGV[1])
if not current or not deduct then
    return {-1, -1}
end
if deduct <= 0 then
    return {current, current}
end
if current <= deduct then
    redis.call("DECRBY", KEYS[1], current)
    return {current, 0}
end
local after = redis.call("DECRBY", KEYS[1], deduct)
return {current, after}
"""


async def write_macaddr_benefit_duration(macaddr: str, benefit: Benefit):
    """写入 MAC 当前权益 duration_config。"""

    # 权益时长配置统一从 benefit.config.duration_config 里读取。
    benefit_config = benefit.config if isinstance(benefit.config, dict) else {}
    duration_config = benefit_config.get("duration_config")
    if not isinstance(duration_config, dict):
        return

    # Redis key 按当前 MAC 维度保存。
    benefit_duration_key = RedisKeys.macaddr_benefit_duration(macaddr)
    duration = duration_config.get("duration")
    refresh = duration_config.get("refresh") or ""
    # duration 非法时不写 Redis。
    if not isinstance(duration, int) or duration <= 0:
        return

    redis_client = await get_redis_client()
    if redis_client is None:
        return

    # 根据 refresh 计算下一次自然刷新边界。
    now = timezone.now()
    ttl_seconds = None
    if refresh == "day":
        next_refresh_at = now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
        ttl_seconds = int((next_refresh_at - now).total_seconds())
    elif refresh == "week":
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        days_until_next_week = 7 - today_start.weekday()
        next_refresh_at = today_start + timedelta(days=days_until_next_week)
        ttl_seconds = int((next_refresh_at - now).total_seconds())
    elif refresh == "month":
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        if month_start.month == 12:
            next_refresh_at = month_start.replace(year=month_start.year + 1, month=1)
        else:
            next_refresh_at = month_start.replace(month=month_start.month + 1)
        ttl_seconds = int((next_refresh_at - now).total_seconds())
    elif refresh == "year":
        year_start = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        next_refresh_at = year_start.replace(year=year_start.year + 1)
        ttl_seconds = int((next_refresh_at - now).total_seconds())

    # 有刷新周期时带 TTL 写入；不刷新时永久保存。
    if isinstance(ttl_seconds, int) and ttl_seconds > 0:
        await redis_client.set(benefit_duration_key, duration, ex=ttl_seconds)
        return

    await redis_client.set(benefit_duration_key, duration)


async def get_user_benefit_duration(user_id: int) -> int:
    """查询用户最新绑定记录对应的权益时长。"""

    # 只取当前仍处于绑定状态的最新记录，和 user_info 的 need_bind 口径保持一致。
    latest_binding = await (
        MacAddressBinding.filter(user_id=user_id, is_bound=True)
        .prefetch_related("mac_address", "benefit")
        .order_by("-last_bind_at", "-bound_at", "-id")
        .first()
    )
    if latest_binding is None:
        return 0

    # 先从最新绑定记录里拿到对应的 MAC 地址。
    mac_address = latest_binding.mac_address
    macaddr = mac_address.mac_address if mac_address and mac_address.mac_address else ""
    if not macaddr:
        return 0

    redis_client = await get_redis_client()
    if redis_client is None:
        return 0

    # 再按 MAC 去 Redis 读取当前权益时长。
    benefit_duration_key = RedisKeys.macaddr_benefit_duration(macaddr)
    duration = await redis_client.get(benefit_duration_key)
    if duration is None:
        # Redis 没有权益时，先判断当前自然月内是否至少绑定过一次。
        now = timezone.now()
        last_bind_at = latest_binding.last_bind_at
        if last_bind_at is None:
            return 0
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        if month_start.month == 12:
            next_month_start = month_start.replace(year=month_start.year + 1, month=1)
        else:
            next_month_start = month_start.replace(month=month_start.month + 1)
        if not (month_start <= last_bind_at < next_month_start):
            return 0

        # 再看这条绑定记录的固定权益窗口是否已经过期。
        benefit_expire_at = latest_binding.benefit_expire_at
        if benefit_expire_at is not None and benefit_expire_at <= now:
            return 0

        # 固定权益窗口未过期时，按绑定记录上的权益重新补发到 Redis。
        benefit = latest_binding.benefit
        if benefit is None:
            return 0

        await write_macaddr_benefit_duration(macaddr, benefit)
        duration = await redis_client.get(benefit_duration_key)
        if duration is None:
            return 0

    # Redis 里取出来的是字符串，这里统一转成 int。
    try:
        return int(duration)
    except (TypeError, ValueError):
        return 0


async def deduct_user_benefit_duration(
    user_id: int,
    duration: int,
    scene: int,
    session_id: str,
) -> dict[str, object]:
    """扣减用户最新绑定记录对应的权益时长。"""

    # 扣减值必须是正整数秒。
    if not isinstance(duration, int) or duration <= 0 or not isinstance(session_id, str) or not session_id.strip():
        return {
            "success": False,
            "request_duration": 0,
            "actual_duration": 0,
            "remaining_duration": 0,
        }

    # 只取当前仍处于绑定状态的最新记录。
    latest_binding = await (
        MacAddressBinding.filter(user_id=user_id, is_bound=True)
        .prefetch_related("mac_address")
        .order_by("-last_bind_at", "-bound_at", "-id")
        .first()
    )
    if latest_binding is None:
        return {
            "success": False,
            "request_duration": duration,
            "actual_duration": 0,
            "remaining_duration": 0,
        }

    # 先拿到这条绑定记录对应的 MAC 地址。
    mac_address = latest_binding.mac_address
    macaddr = mac_address.mac_address if mac_address and mac_address.mac_address else ""
    if not macaddr:
        return {
            "success": False,
            "request_duration": duration,
            "actual_duration": 0,
            "remaining_duration": 0,
        }

    redis_client = await get_redis_client()
    if redis_client is None:
        return {
            "success": False,
            "request_duration": duration,
            "actual_duration": 0,
            "remaining_duration": 0,
        }

    # 先走现有查询链路，确保 Redis 缺失时会按既有规则尝试补发权益。
    current_duration = await get_user_benefit_duration(user_id)
    if current_duration <= 0:
        return {
            "success": False,
            "request_duration": duration,
            "actual_duration": 0,
            "remaining_duration": 0,
        }

    benefit_duration_key = RedisKeys.macaddr_benefit_duration(macaddr)
    deduct_result = await redis_client.eval(
        DEDUCT_BENEFIT_DURATION_LUA,
        1,
        benefit_duration_key,
        duration,
    )

    # Lua 一次性返回扣减前和扣减后的值，避免并发下日志口径不准。
    if not isinstance(deduct_result, list) or len(deduct_result) != 2:
        return {
            "success": False,
            "request_duration": duration,
            "actual_duration": 0,
            "remaining_duration": current_duration,
        }

    try:
        before_duration = int(deduct_result[0])
        remaining_duration = int(deduct_result[1])
    except (TypeError, ValueError):
        return {
            "success": False,
            "request_duration": duration,
            "actual_duration": 0,
            "remaining_duration": current_duration,
        }

    if before_duration < 0 or remaining_duration < 0:
        return {
            "success": False,
            "request_duration": duration,
            "actual_duration": 0,
            "remaining_duration": current_duration,
        }

    # 实际扣减值按 Redis 原子脚本返回结果反推，避免超扣时口径不准。
    actual_duration = before_duration - remaining_duration

    # 扣减成功后补一条扣费审计日志。
    await BenefitDeductionLog.create(
        user_id=user_id,
        mac_address_id=latest_binding.mac_address_id,
        session_id=session_id.strip(),
        scene=scene,
        request_duration=duration,
        actual_duration=actual_duration,
        before_duration=before_duration,
        after_duration=remaining_duration,
    )

    return {
        "success": True,
        "request_duration": duration,
        "actual_duration": actual_duration,
        "remaining_duration": remaining_duration,
    }
