from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from redis import RedisError
from starlette.exceptions import HTTPException as StarletteHTTPException
from tortoise import Tortoise
from tortoise.exceptions import DoesNotExist, IntegrityError, OperationalError

from app.common.exception.exception_handlers import base_api_exception_handler, validation_exception_handler, \
    http_exception_handler, tortoise_exception_handler, redis_exception_handler, general_exception_handler
from app.common.exception.exceptions import BaseAPIException
from app.common.middlewares.jwt_admin_middleware import AdminJWTMiddleware
from app.common.middlewares.request_response_logging_middleware import RequestResponseLoggingMiddleware
from app.db.tortise_settings import TORTOISE_ORM
from app.db.redis import init_redis_pool, close_redis_pool
from app.router.router_admin import router_admin
from app.core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Import broker here to avoid circular imports
    from app.worker.broker import broker

    # Startup
    await Tortoise.init(config=TORTOISE_ORM)
    await init_redis_pool()

    # Start worker broker (only in non-worker processes)
    if not broker.is_worker_process:
        await broker.startup()

    yield

    # Shutdown
    if not broker.is_worker_process:
        await broker.shutdown()

    await close_redis_pool()
    await Tortoise.close_connections()


app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
    lifespan=lifespan
)

app.add_middleware(AdminJWTMiddleware)
app.add_middleware(RequestResponseLoggingMiddleware)

# 注册异常处理器 - 按优先级顺序，最具体的异常在前面
app.add_exception_handler(BaseAPIException, base_api_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(DoesNotExist, tortoise_exception_handler)
app.add_exception_handler(IntegrityError, tortoise_exception_handler)
app.add_exception_handler(OperationalError, tortoise_exception_handler)
app.add_exception_handler(RedisError, redis_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

app.include_router(router_admin, prefix="/admin/api")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host=settings.host, port=settings.port, reload=settings.debug)