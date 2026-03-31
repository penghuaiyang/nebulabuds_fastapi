"""Apple 订阅支付服务."""
import json
import time
from typing import Tuple

import httpx

from app.common.utils.log_utils import log_util
from app.db.redis import get_redis_client
from app.models.models import User, PurchasedRecord

logger = log_util.get_logger("apple_pay_service")

APPLE_VALIDATION_URL_PRODUCTION = "https://buy.itunes.apple.com/verifyReceipt"
APPLE_VALIDATION_URL_SANDBOX = "https://sandbox.itunes.apple.com/verifyReceipt"

VIP_PRODUCT_IDS = {
    "com.palmzen.NebulaBuds.seasonVip",
    "com.palmzen.NebulaBuds.seasonVip2",
    "com.palmzen.NebulaBuds.seasonVip3",
    "com.palmzen.NebulaBuds.yearVIP",
    "com.palmzen.NebulaBuds.yearVIP2",
    "com.palmzen.NebulaBuds.yearVIP3",
}

RECORD_PRODUCT_IDS = {
    "com.palmzen.NebulaBuds.300mins",
    "com.palmzen.NebulaBuds.720mins",
    "com.palmzen.NebulaBuds.1800mins",
}

VIP_PRICE_MAP = {
    "com.palmzen.NebulaBuds.seasonVip": 98,
    "com.palmzen.NebulaBuds.seasonVip2": 98,
    "com.palmzen.NebulaBuds.seasonVip3": 98,
    "com.palmzen.NebulaBuds.yearVIP": 198,
    "com.palmzen.NebulaBuds.yearVIP2": 198,
    "com.palmzen.NebulaBuds.yearVIP3": 198,
}

RECORD_PRICE_MAP = {
    "com.palmzen.NebulaBuds.300mins": 98,
    "com.palmzen.NebulaBuds.720mins": 198,
    "com.palmzen.NebulaBuds.1800mins": 398,
}


class ApplePayService:
    """Apple 订阅支付服务类."""

    @staticmethod
    async def verify_receipt(receipt_data: str, use_sandbox: bool = False) -> Tuple[bool, str | None, str | None]:
        """验证 Apple 支付收据.
        
        Args:
            receipt_data: Apple 支付返回的 receipt 数据
            use_sandbox: 是否使用沙箱环境验证
            
        Returns:
            (验证成功, product_id, transaction_id) 或 (False, None, None)
        """
        validation_url = (
            APPLE_VALIDATION_URL_SANDBOX if use_sandbox else APPLE_VALIDATION_URL_PRODUCTION
        )
        
        post_data = {"receipt-data": receipt_data}
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    validation_url,
                    json=post_data,
                )
                response_data = response.json()
                
            logger.info(f"Apple receipt verification response: {response_data}")
            
            if response_data.get("status") == 0:
                receipt_info = response_data.get("receipt", {})
                in_app = receipt_info.get("in_app", [])
                if in_app:
                    product_id = in_app[0].get("product_id")
                    transaction_id = in_app[0].get("transaction_id")
                    return True, product_id, transaction_id
                    
            return False, None, None
            
        except httpx.TimeoutException:
            logger.error("Apple receipt verification timeout")
            return False, None, None
        except Exception as e:
            logger.error(f"Apple receipt verification error: {e}")
            return False, None, None

    @staticmethod
    async def _get_user_from_db(userid: int) -> User | None:
        """从数据库获取用户."""
        return await User.filter(userid=userid).first()

    @staticmethod
    async def _get_user_vip(userid: int) -> int:
        """获取用户 VIP 到期时间戳."""
        user = await ApplePayService._get_user_from_db(userid)
        if user:
            return user.vip or 0
        return 0

    @staticmethod
    async def _get_user_record_rest_time(userid: int) -> int:
        """获取用户录音剩余时长(秒)."""
        redis_client = await get_redis_client()
        if redis_client:
            rest_time = await redis_client.get(f"29:record:user:{userid}:rest")
            if rest_time:
                return int(rest_time)
        return 0

    @staticmethod
    async def _set_user_vip(userid: int, vip_timestamp: int) -> None:
        """设置用户 VIP 到期时间."""
        await User.filter(userid=userid).update(vip=vip_timestamp)
        redis_client = await get_redis_client()
        if redis_client:
            await redis_client.set(f"30:user:profile:{userid}", json.dumps({"vip": vip_timestamp}))

    @staticmethod
    async def _add_record_rest_time(userid: int, add_seconds: int) -> int:
        """增加用户录音剩余时长."""
        redis_client = await get_redis_client()
        if redis_client:
            key = f"29:record:user:{userid}:rest"
            current = await redis_client.get(key)
            current = int(current) if current else 0
            new_rest = current + add_seconds
            await redis_client.set(key, new_rest)
            return new_rest
        return 0

    @staticmethod
    async def _add_payment_record(
        userid: int,
        money: float,
        pay_type: int,
        transaction_id: str,
        pay_from: str,
        pay_for: str,
    ) -> None:
        """添加支付记录."""
        await PurchasedRecord.create(
            userid=userid,
            price=money,
            payType=pay_type,
            tradeNo=transaction_id,
            time=int(time.time() * 1000),
            payFrom=pay_from,
            payFor=pay_for,
        )

    @classmethod
    async def process_payment(
        cls,
        userid: int,
        receipt_data: str,
    ) -> dict:
        """处理 Apple 支付.
        
        Args:
            userid: 用户 ID
            receipt_data: Apple 支付收据
            
        Returns:
            包含 vip, restTime, code 的字典
        """
        success, product_id, transaction_id = await cls.verify_receipt(receipt_data)
        
        if not success:
            return {"code": -1}
        
        logger.info(f"Apple payment verified: userid={userid}, product_id={product_id}, transaction_id={transaction_id}")
        
        if product_id in VIP_PRODUCT_IDS:
            return await cls._process_vip_payment(userid, product_id, transaction_id)
        elif product_id in RECORD_PRODUCT_IDS:
            return await cls._process_record_payment(userid, product_id, transaction_id)
        else:
            logger.warning(f"Unknown product_id: {product_id}")
            return {"code": -1}

    @classmethod
    async def _process_vip_payment(
        cls,
        userid: int,
        product_id: str,
        transaction_id: str,
    ) -> dict:
        """处理 VIP 订阅支付."""
        money = VIP_PRICE_MAP.get(product_id, 0)
        pay_for = "vip"
        
        current_vip = await cls._get_user_vip(userid)
        current_time = int(time.time())
        
        if current_time > current_vip:
            new_vip = current_time
        else:
            new_vip = current_vip
        
        if money == 98:
            new_vip = new_vip + 90 * 24 * 60 * 60
            rest_time = await cls._add_record_rest_time(userid, 4 * 60 * 60)
        elif money == 198:
            new_vip = new_vip + 365 * 24 * 60 * 60
            rest_time = await cls._add_record_rest_time(userid, 8 * 60 * 60)
        else:
            rest_time = await cls._add_record_rest_time(userid, 0)
        
        await cls._set_user_vip(userid, new_vip)
        await cls._add_payment_record(userid, money, 6, transaction_id, "ios", pay_for)
        
        logger.info(f"VIP payment processed: userid={userid}, new_vip={new_vip}, rest_time={rest_time}")
        
        return {"vip": new_vip, "restTime": rest_time, "code": 1}

    @classmethod
    async def _process_record_payment(
        cls,
        userid: int,
        product_id: str,
        transaction_id: str,
    ) -> dict:
        """处理录音时长购买支付."""
        money = RECORD_PRICE_MAP.get(product_id, 0)
        pay_for = "record"
        
        current_vip = await cls._get_user_vip(userid)
        
        if money == 98:
            rest_time = await cls._add_record_rest_time(userid, 5 * 60 * 60)
        elif money == 198:
            rest_time = await cls._add_record_rest_time(userid, 12 * 60 * 60)
        elif money == 398:
            rest_time = await cls._add_record_rest_time(userid, 30 * 60 * 60)
        else:
            rest_time = await cls._add_record_rest_time(userid, 0)
        
        await cls._add_payment_record(userid, money, 6, transaction_id, "ios", pay_for)
        
        logger.info(f"Record payment processed: userid={userid}, rest_time={rest_time}")
        
        return {"vip": current_vip, "restTime": rest_time, "code": 1}
