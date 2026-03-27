# 变更：收口按 `userid` 读取用户缓存

## 变更原因
- 登录链路当前仍直接按 `userid` 查询 `user` 表，热点用户登录会持续打到 MySQL。
- `user.userid` 目前没有数据库索引，缓存未命中时查询成本偏高。
- 项目已经有 `UserService` 的 Cache-Aside 约定，适合把按 `userid` 的用户读取统一收口到服务层。

## 变更内容
- 新增 `UserService.get_user_by_userid(userid)`，统一走 Redis 读穿缓存。
- 新增按 `userid` 存储用户详情的 Redis key，并把用户缓存扩展为同时写入 `deviceid` 和 `userid` 两份 key。
- 将 `LoginService.login()` 的用户读取改为依赖 `UserService`，不再直接调用 `User.filter(userid=...)`。
- 给 `user.userid` 增加普通索引，并提供对应迁移。

## 影响范围
- 受影响规范：`user-cache`
- 受影响代码：`app/services/user_service.py`、`app/services/login_service.py`、`app/db/redis_keys.py`、`app/models/models.py`、`migrations/models/`
