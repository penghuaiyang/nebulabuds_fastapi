# NebulaBuds FastAPI 重构迁移指南

本文档为 AI 助手提供从 Tornado 迁移到 FastAPI 的规范指导。

---

## 项目架构

### 分层结构
```
app/
├── view/           # 接口入口（View Handler）
├── services/        # 业务逻辑层
├── models/          # 数据模型（Tortoise ORM）
├── router/         # 路由注册
├── db/             # 数据库连接
│   ├── redis.py    # Redis 连接池管理
│   └── redis_keys.py # Redis Key 定义
└── common/
    ├── utils/      # 工具函数
    └── middlewares/# 中间件
```

### 核心模式
- **Cache-Aside 模式**：MySQL 为主存储，Redis 为只读缓存
- **连接池复用**：所有 Redis 操作使用 `get_redis_client()`
- **分层架构**：View → Service → Model

---

## View Handler 规范

### 标准模板
```python
from pydantic import BaseModel, Field
from fastapi import Request
from app.common.utils.jwt_utils import no_auth_required
from app.services.{业务名}_service import {业务名}Service

class {业务名}Schemas(BaseModel):
    field1: str = Field(..., min_length=1, max_length=64, description="必填字段")
    field2: Optional[int] = Field(None, description="可选字段")

@no_auth_required
async def {业务名}(data: {业务名}Schemas, request: Request) -> dict:
    service = {业务名}Service()
    result = await service.{方法}(...)
    return {"code": 1, "data": result}
```

### 关键点
1. **必填字段**：`Field(..., min_length=1, max_length=N)`
2. **可选字段**：`Optional[T] = Field(None, ...)`
3. **签名字段**：使用 `alias="pass"`
4. **响应格式**：`{"code": 1, "data": {...}}` 或 `{"code": 0, "error": "..."}`

---

## Service 层规范

### 标准模板
```python
import redis.asyncio as redis
from app.db.redis import get_redis_client
from app.models.models import {Model}
from app.common.utils.log_utils import log_util

logger = log_util.get_logger("{业务名}_service")

class {业务名}Service:
    @staticmethod
    async def _get_redis() -> redis.Redis:
        client = await get_redis_client()
        if client is None:
            raise RuntimeError("Redis connection not available")
        return client

    @classmethod
    async def {方法}(cls, ...) -> dict:
        # 1. 查缓存
        cached = await cls.get_cache(key)
        if cached:
            return cached

        # 2. 查数据库
        entity = await {Model}.filter(...).first()

        # 3. 回填缓存
        await cls.set_cache(key, entity)

        return await entity.to_dict()
```

### 缓存操作规范
```python
# 查缓存
async def get_cache(cls, key: str) -> Optional[dict]:
    try:
        client = await cls._get_redis()
        cached = await client.get(key)
        return json.loads(cached) if cached else None
    except Exception as e:
        logger.warning(f"Redis get failed: {e}")
        return None

# 写缓存（TTL: 24小时）
async def set_cache(cls, key: str, data: dict) -> None:
    try:
        client = await cls._get_redis()
        await client.setex(key, 86400, json.dumps(data))
    except Exception as e:
        logger.warning(f"Redis set failed: {e}")

# 删除缓存
async def invalidate_cache(cls, key: str) -> None:
    try:
        client = await cls._get_redis()
        await client.delete(key)
    except Exception as e:
        logger.warning(f"Redis delete failed: {e}")
```

---

## 迁移检查清单

### 必检项
| 原版实现 | FastAPI 迁移 |
|----------|--------------|
| `params['key']` | Pydantic Schema `Field` |
| `utils.check()` | `@check_params` 装饰器或函数 |
| `@jwt_required` | `@auth_required` |
| 手动 Redis 连接 | `get_redis_client()` |
| 手动 SQL | Tortoise ORM |

### 优化项
- [ ] 拆分 Service 层
- [ ] 提取工具函数到 `app/common/utils/`
- [ ] 添加缓存逻辑
- [ ] 完善日志记录
- [ ] 添加类型注解

### 兼容性
- [ ] 保留原接口路径
- [ ] 保持 `{"code": N, ...}` 响应格式
- [ ] 错误码语义一致

---

## Redis Key 规范

在 `app/db/redis_keys.py` 中定义：
```python
class RedisKeys:
    # 格式：{业务}_{主键}_{标识}
    USER_ID_SEQ = "user_id_seq"

    @staticmethod
    def device_user_id(device_id: str):
        return f"device_userid:{device_id}"
```

---

## 代码风格

- **缩进**：4 空格
- **命名**：snake_case（变量/函数），PascalCase（类）
- **类型注解**：必填
- **docstring**：精简
- **日志**：使用 `log_util.get_logger()`
