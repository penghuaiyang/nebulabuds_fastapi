from agno.models.openai.like import OpenAILike
from app.core.config import settings

qwen_model = OpenAILike(
    id=settings.qwen_model_id,
    api_key=settings.qwen_api_key,
    base_url=settings.qwen_base_url
)
