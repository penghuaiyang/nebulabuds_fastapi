from agno.models.openai.like import OpenAILike
from agno.agent import Agent
from app.common.llm.model_client import qwen_model
from app.common.utils.log_utils import log_util

logger = log_util.get_logger("translate")


def get_instructions(agent: Agent) -> str:
    return f"你是翻译助手，将文本:{agent.source_text}翻译成{agent.target_language}"


agent = Agent(
    model=qwen_model,
    instructions=get_instructions,
    retries=3,
    exponential_backoff=True,
)


async def translate_text(source_text: str, target_language: str) -> str:
    try:
        agent.source_text = source_text
        agent.target_language = target_language
        response = await agent.arun("")
        return response.content
    except Exception as e:
        logger.info(e)
        return source_text


