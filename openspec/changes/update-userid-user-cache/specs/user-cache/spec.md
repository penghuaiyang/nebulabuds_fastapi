## ADDED Requirements
### Requirement: 按 `userid` 读取用户缓存
系统 MUST 提供统一的按 `userid` 读取用户信息接口，并优先从 Redis 读取缓存。

#### Scenario: Redis 命中用户缓存
- **WHEN** 服务层按 `userid` 读取用户且 Redis 中存在对应缓存
- **THEN** 系统直接返回缓存中的用户信息
- **AND** 系统不再查询 MySQL

#### Scenario: Redis 未命中用户缓存
- **WHEN** 服务层按 `userid` 读取用户且 Redis 中不存在对应缓存
- **THEN** 系统回源 MySQL 查询 `user` 表
- **AND** 当用户存在时将用户信息回填到 Redis

#### Scenario: Redis 不可用时降级
- **WHEN** 服务层按 `userid` 读取用户且 Redis 访问失败
- **THEN** 系统记录告警日志
- **AND** 系统继续回源 MySQL 查询用户信息

### Requirement: 用户缓存写入覆盖双索引
系统 MUST 在写入用户缓存时同时维护 `deviceid` 和 `userid` 两类缓存 key。

#### Scenario: 新用户创建或老用户登录后写缓存
- **WHEN** 系统写入用户缓存
- **THEN** 系统同时写入基于 `deviceid` 和基于 `userid` 的缓存 key

### Requirement: `user.userid` 查询可走索引
系统 MUST 为 `user.userid` 查询提供数据库索引，以降低缓存未命中时的查询成本。

#### Scenario: 部署索引迁移
- **WHEN** 数据库执行本次变更对应的迁移
- **THEN** `user` 表新增 `userid` 普通索引
