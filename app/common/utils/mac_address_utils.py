"""MAC 地址工具函数"""
import re
from typing import Optional

MAC_ADDRESS_PATTERN = re.compile(r"^([0-9A-F]{2}:){5}[0-9A-F]{2}$", re.IGNORECASE)


def normalize_mac_address(value: Optional[str]) -> str:
    """归一化 MAC 地址（大写、冒号分隔）"""
    if value is None:
        return ""
    cleaned = str(value).strip().upper()
    if not cleaned:
        return ""
    cleaned = cleaned.replace("-", ":")
    if ":" not in cleaned and len(cleaned) == 12:
        if re.fullmatch(r"[0-9A-F]{12}", cleaned):
            cleaned = ":".join(cleaned[i:i + 2] for i in range(0, 12, 2))
    return cleaned


def is_valid_mac_address(value: str) -> bool:
    """验证 MAC 地址格式（XX:XX:XX:XX:XX:XX）"""
    return bool(MAC_ADDRESS_PATTERN.fullmatch(value))


def get_mac_address_unique_scope(customer_id: int, mac_type: int) -> int:
    """计算 MAC 地址唯一性作用域。"""
    return 0 if mac_type == 2 else customer_id
