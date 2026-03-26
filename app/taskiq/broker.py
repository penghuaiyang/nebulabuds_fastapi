"""
Taskiq broker configuration.

This module sets up the Redis-based broker for distributed task processing.
"""
from taskiq_redis import ListQueueBroker, RedisAsyncResultBackend
import taskiq_fastapi
from app.core.config import settings

# Create result backend with 1 hour expiration
result_backend = RedisAsyncResultBackend(
    redis_url=settings.result_backend_url,
    result_ex_time=3600,  # Results expire after 1 hour
)

# Create broker with Redis List Queue for reliable task delivery
# ListQueueBroker uses Redis lists for task queuing
broker = ListQueueBroker(
    url=settings.broker_url,
).with_result_backend(result_backend)

# Initialize FastAPI integration
# This enables dependency injection and proper lifecycle management
taskiq_fastapi.init(broker, "app.main:app")


# Initialize the Scheduler
# LabelScheduleSource: Reads schedule labels from task decorators (static schedules)
# RedisScheduleSource: Allows storing schedules in Redis for dynamic runtime scheduling
from taskiq import TaskiqScheduler
from taskiq_redis import RedisScheduleSource
from taskiq.schedule_sources import LabelScheduleSource

scheduler = TaskiqScheduler(
    broker=broker,
    sources=[
        LabelScheduleSource(broker),  # Required for @broker.task(schedule=[...])
        RedisScheduleSource(settings.broker_url),  # For dynamic scheduling at runtime
    ],
)
