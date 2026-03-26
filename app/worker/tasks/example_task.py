"""
Example task for testing.
"""
from app.worker.broker import broker
from app.common.utils.log_utils import log_util

logger = log_util.get_logger("queue.tasks.example")


@broker.task
async def example_task(name: str) -> str:
    """
    Simple example task for testing.
    
    Args:
        name: Name to greet
        
    Returns:
        Greeting message
    """
    logger.info(f"Processing task for: {name}")
    return f"Hello, {name}!"