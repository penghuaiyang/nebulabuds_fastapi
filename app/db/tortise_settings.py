from app.core.config import settings

TORTOISE_ORM = {
    "connections": {
        "default": settings.mysql_dsn
    },
    "apps": {
        "models": {
            "models": ["app.models.models", "aerich.models"],
            "default_connection": "default",
        }
    },
    "use_tz": False,
    "timezone": "Asia/Shanghai"
}
