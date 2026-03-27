# NebulaBuds FastAPI 重构迁移规范

## 全局规则
- 请全程使用中文交流
- 每次修改完代码都先详细说明修改内容，最后用 5-20 字做一个修改概括

---

## 一、架构模式

### 1.1 分层结构
```
app/view/        # 接口入口（接收请求、参数校验）
app/services/    # 业务逻辑层（核心处理）
app/models/      # 数据模型层（Tortoise ORM）
app/common/utils/# 工具函数层（复用逻辑）
```

### 1.2 Cache-Aside 缓存模式
```
读流程: 查 Redis → 未命中 → 查 MySQL → 回填 Redis → 返回
写流程: 写 MySQL → 删除 Redis 缓存（而非更新）
```

### 1.3 连接池复用
- Redis：使用 `app/db/redis.py` 的 `get_redis_client()` 获取连接池中的客户端
- MySQL：使用 Tortoise ORM 的异步连接

---

## 二、文件命名规范

| 层次 | 命名规范 | 示例 |
|------|----------|------|
| View Handler | `{业务名}_handler.py` | `join_handler.py` |
| Schema | `{业务名}_schemas.py`（可内置） | - |
| Service | `{业务名}_service.py` | `user_service.py` |
| Utils | `{功能}_utils.py` | `join_utils.py` |

---

## 三、View Handler 编写规范

### 3.1 基本结构
```python
from pydantic import Field
from fastapi import Request

from app.common.schemas.base import BaseSchema
from app.common.utils.jwt_utils import no_auth_required
from app.services.{业务名}_service import {业务名}Service

class {业务名}Schemas(BaseSchema):
    """请求参数模型（继承 BaseSchema，自动包含签名字段）"""
    field1: str = Field(..., min_length=1, max_length=64, description="字段说明")
    field2: Optional[int] = Field(None, description="可选字段")

@no_auth_required  # 或 @auth_required
async def {业务名}(data: {业务名}Schemas, request: Request) -> dict:
    """处理{业务名}请求"""
    service = {业务名}Service()
    result = await service.{业务方法}(...)
    return {"code": 1, "data": result}
```

### 3.2 Schema 设计原则
- 必填字段：`Field(..., min_length=1, max_length=N)`
- 可选字段：`Optional[T] = Field(None, ...)`
- 添加清晰的 `description`
- **重要**：所有需要签名校验的 Schema 必须继承 `BaseSchema`

### 3.3 响应格式
```python
# 成功
return {"code": 1, "data": {...}}

# 失败
return {"code": 0, "error": "错误信息"}
```

### 3.4 错误处理
```python
try:
    result = await service.method(...)
except BusinessException as e:
    return {"code": e.code, "error": e.message}
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    return {"code": -1, "error": str(e)}
```

### 3.5 签名字段基类
所有需要签名校验的接口 Schema 必须继承 `BaseSchema`：
```python
from app.common.schemas.base import BaseSchema

class {业务名}Schemas(BaseSchema):
    # 无需重复定义 pass_ 字段，已从 BaseSchema 继承
    field1: str = Field(..., description="...")
```

`BaseSchema` 位于 `app/common/schemas/base.py`，包含签名字段定义。

---

## 四、Service 层编写规范

### 4.1 基本结构
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
    async def {业务方法}(cls, params: dict) -> dict:
        # 1. 业务逻辑
        # 2. 数据处理
        # 3. 返回结果
```

### 4.2 缓存操作
```python
# 获取缓存
async def get_cache(cls, key: str) -> Optional[dict]:
    try:
        client = await cls._get_redis()
        cached = await client.get(key)
        return json.loads(cached) if cached else None
    except Exception as e:
        logger.warning(f"Redis get failed: {e}")
        return None

# 设置缓存（24小时过期）
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

### 4.3 日志规范
- 使用 `log_util.get_logger("{模块名}")` 创建 logger
- INFO：正常业务流程
- WARNING：可降级的异常（如缓存失败）
- ERROR：不可恢复的错误

---

## 五、路由注册规范

在 `app/router/router.py` 中注册：
```python
from app.view.{业务名}_handler import {业务名}

router.add_api_route(
    path="/{业务名}/",
    endpoint={业务名},
    methods=["POST"],  # 或 ["GET", "POST"]
)
```

---

## 六、从 Tornado 到 FastAPI 的迁移检查清单

### 6.1 必检项
- [ ] 参数校验：Tornado `params['key']` → FastAPI Pydantic Schema
- [ ] 签名校验：`utils.check()` → 装饰器或函数
- [ ] 用户认证：`@jwt_required` → `@auth_required`
- [ ] Redis 操作：手动创建连接 → `get_redis_client()`
- [ ] MySQL 操作：手动 SQL → Tortoise ORM 模型

### 6.2 优化项
- [ ] 拆分 Service 层
- [ ] 提取复用工具函数
- [ ] 添加缓存逻辑
- [ ] 完善日志记录
- [ ] 补充类型注解

### 6.3 兼容性
- [ ] 保留原接口路径（如 `/join/`）
- [ ] 保持响应格式一致（`{"code": N, ...}`）
- [ ] 错误码语义一致

---

## 七、Redis Key 命名规范

在 `app/db/redis_keys.py` 中定义：
```python
class RedisKeys:
    # 通用格式：{业务}_{主键}_{标识}
    USER_ID_SEQ = "user_id_seq"

    @staticmethod
    def device_user_id(device_id: str):
        return f"device_userid:{device_id}"
```

---

## 八、提交规范

- 提交信息：简洁动词开头，如 `完成 join 接口迁移`
- 每个 commit 只做一件事
- 包含测试说明
