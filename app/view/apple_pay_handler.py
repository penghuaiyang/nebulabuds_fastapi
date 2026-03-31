"""Apple Pay 处理器."""
from fastapi import Request

from app.common.schemas.apple_pay_schema import ApplePayRequestSchema
from app.common.utils.log_utils import log_util
from app.services.apple_pay_service import ApplePayService

logger = log_util.get_logger("apple_pay_handler")


async def apple_pay(
    data: ApplePayRequestSchema,
    request: Request,
) -> dict:
    """处理 Apple 支付请求.
    
    支持 POST 请求，接收 userid 和 receipt_data，
    验证 Apple 支付收据并更新用户 VIP 或录音时长。
    
    Args:
        data: Apple Pay 请求参数
        request: FastAPI 请求对象
        
    Returns:
        包含 vip, restTime, code 的响应字典
    """
    logger.info(f"Apple Pay request: userid={data.userid}, receipt_data={data.receipt_data[:50]}...")
    
    try:
        result = await ApplePayService.process_payment(
            userid=data.userid,
            receipt_data=data.receipt_data,
        )
        logger.info(f"Apple Pay result: {result}")
        return result
    except Exception as e:
        logger.exception(f"Apple Pay error: {e}")
        return {"code": -3, "error": str(e)}
