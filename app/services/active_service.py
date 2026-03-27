"""Active（V1）设备激活服务."""
import os
import time
from typing import Any, Dict, Optional, Tuple

from app.common.utils.log_utils import log_util
from app.models.models import (
    Mac,
    MacFalse,
    ActiveRecord,
    Buds,
    DeviceHiddenFunction,
    User,
)

logger = log_util.get_logger("active_service")

# 常量定义
MAX_BIND_USERS = 3
ACTIVE_PERIOD_SECONDS = 315360000  # 1年

# 绑定上限豁免白名单
BIND_LIMIT_BYPASS = {
    "y7s1j0Vu": {"FF:FF:00:01:1F:64"},
}


def is_bind_limit_bypassed(clientid: str, mac_addr: str) -> bool:
    """检查是否在绑定限制豁免白名单中."""
    mac_whitelist = BIND_LIMIT_BYPASS.get(clientid, set())
    return mac_addr in mac_whitelist or "*" in mac_whitelist


def _safe_int(value: Any, default: int = 0) -> int:
    """安全转换为int."""
    if value is None:
        return default
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


class ActiveService:
    """Active（V1）设备激活服务类."""

    @classmethod
    async def activate(
        cls,
        bt_name: str,
        clientid: str,
        mac_addr: str,
        userid: Optional[int] = None,
    ) -> Tuple[int, Dict[str, Any]]:
        """处理 V1 设备激活.

        Args:
            bt_name: 蓝牙设备名称
            clientid: 客户端ID
            mac_addr: MAC地址
            userid: 用户ID

        Returns:
            Tuple[code, data]
            - code=1: 激活成功
            - code=2: 已激活
            - code=-1: MAC地址不在激活列表
            - code=-2: 超过激活期限
            - code=-3: clientid不在授权列表
            - code=-4: 超过绑定用户限制
            - code=-5: userid为空
        """
        try:
            # 设置时区
            os.environ["TZ"] = "Asia/Shanghai"

            # 检查 clientid 是否授权
            if not clientid:
                return -3, {"code": -3}

            # TODO: 需要实现 clientid 授权检查逻辑
            # 目前简化处理，直接检查 MAC 是否存在
            mac_info = await Mac.filter(macAddr=mac_addr, clientCode=clientid).first()
            if not mac_info:
                await cls._add_mac_false_record(clientid, mac_addr)
                return -1, {"code": -1}

            # 获取激活信息
            active_time = mac_info.activeTime or 0
            active_status = mac_info.active or 0
            mac_type = mac_info.macType or 1

            current_ts = int(time.time())

            # 检查激活期限
            if active_status == 1 and (current_ts - (active_time // 1000)) > ACTIVE_PERIOD_SECONDS:
                await cls._add_mac_false_record(clientid, mac_addr)
                return -2, {"code": -2}

            # 检查 userid
            if userid is None:
                await cls._add_mac_false_record(clientid, mac_addr)
                return -5, {"code": -5}

            # 获取隐藏功能列表
            hidden_functions = await cls.get_hidden_function(bt_name)

            # 获取功能信息
            func_info = await cls.get_func_info(userid, bt_name, mac_type)

            # 更新激活状态
            if active_status != 1:
                await Mac.filter(macAddr=mac_addr, clientCode=clientid).update(
                    active=1, activeTime=int(time.time() * 1000)
                )
                await cls._activate_mac(clientid, mac_addr)
                await cls._add_mac_active_record(clientid, mac_addr, userid, active_type=1)

            if active_status == 1:
                return 2, {
                    "code": 2,
                    "hidden_function_ids": hidden_functions,
                    "func_info": func_info,
                }

            return 1, {
                "code": 1,
                "hidden_function_ids": hidden_functions,
                "func_info": func_info,
            }

        except Exception as exc:
            logger.exception(f"Active error: {exc}")
            return -3, {"code": -3, "error": str(exc)}

    @classmethod
    async def get_hidden_function(cls, bt_name: str) -> list:
        """获取设备的隐藏功能列表."""
        if not bt_name:
            return []

        hidden_map = {2: "3", 3: "3", 8: "3"}
        device_ids = await Buds.filter(blName__contains=bt_name).values_list(
            "deviceType", flat=True
        )

        first_hidden_ids = [hidden_map[d] for d in device_ids if d in hidden_map]

        hidden_ids = await DeviceHiddenFunction.filter(
            device_name=bt_name
        ).values_list("hidden_function", flat=True)

        return list(set(hidden_ids + first_hidden_ids))

    @classmethod
    async def get_func_info(cls, userid: Optional[int], bt_name: str, mac_type: int) -> dict:
        """获取功能信息."""
        return {
            "macType": mac_type,
            "btName": bt_name,
        }

    @staticmethod
    async def _add_mac_false_record(clientid: str, mac_addr: str, active_type: int = 1) -> None:
        """添加 MacFalse 记录."""
        try:
            existing = await MacFalse.filter(
                clientCode=clientid, macAddr=mac_addr
            ).first()
            if existing:
                return

            import_time = int(time.time() * 1000)
            await MacFalse.create(
                clientCode=clientid,
                macAddr=mac_addr,
                importTime=import_time,
                activeType=active_type,
            )
        except Exception as exc:
            logger.error(f"Add MacFalse record failed: {exc}")

    @staticmethod
    async def _activate_mac(clientid: str, mac_addr: str) -> None:
        """激活 MAC 地址."""
        try:
            active_time = int(time.time() * 1000)
            await Mac.filter(clientCode=clientid, macAddr=mac_addr).update(
                active=1, activeTime=active_time
            )
        except Exception as exc:
            logger.error(f"Activate MAC failed: {exc}")

    @staticmethod
    async def _add_mac_active_record(
        clientid: str, mac_addr: str, userid: int, active_type: int
    ) -> None:
        """添加 MAC 激活记录."""
        try:
            existing = await ActiveRecord.filter(
                mac=mac_addr, userid=userid, activeType=active_type
            ).first()
            if existing:
                return

            active_time = int(time.time() * 1000)
            await ActiveRecord.create(
                clientid=clientid,
                mac=mac_addr,
                userid=userid,
                time=active_time,
                activeType=active_type,
            )
        except Exception as exc:
            logger.error(f"Add MAC active record failed: {exc}")
