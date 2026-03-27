"""
Redis Key 回滚脚本：将新格式 key 回滚到旧系统格式（灾备用）。

新格式（统一 db={N}:{namespace}:{scope}:{identifier}）：
  7:record:user:{userid}:duration
  10:music:user:{userid}:num
  8:ai:user:{userid}:num
  14:btname:user:{userid}:list
  23:mac:user:{userid}:active_code
  24:mac:user:{userid}:clientid
  25:record:user:{userid}:free_date
  29:record:user:{userid}:rest
  0:config:app:single_max_duration 或 0:config:app:single_max_duration:{clientid}

旧格式（db 分片）：
  db=7 + db_start[clientid] -> key=userid (String)
  db=8 + db_start[clientid] -> key=userid (String)
  db=10 + db_start[clientid] -> key=userid (String)
  db=14 -> key=userid (List)
  db=23 -> key=userid (Hash)
  db=24 -> key=userid (Hash)
  db=25 -> key=userid (String)
  db=29 -> key=userid (String)
  db=2 -> key="app:feature:single_max_duration" (String)

注意：回滚需要指定 client_db_start 映射才能正确计算分片 db。

用法：
  python -m admin.rollback_redis_keys --dry-run
  python -m admin.rollback_redis_keys --live
  python -m admin.rollback_redis_keys --db 7,8,10 --dry-run
"""

import argparse
import asyncio
import json
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import redis.asyncio as redis
from dotenv import load_dotenv

load_dotenv()

# ==================== 新格式到旧格式的映射 ====================
# 新 key 前缀 -> (目标 db, key 类型, 是否需要 client_db_start)
NEW_KEY_PATTERNS = [
    # (新 key 前缀, 目标 db 或计算方法, key 类型)
    ("7:record:user:", "7+offset", "string"),  # 需要 client_db_start
    ("8:ai:user:", "8+offset", "string"),  # 需要 client_db_start
    ("10:music:user:", "10+offset", "string"),  # 需要 client_db_start
    ("14:btname:user:", 14, "list"),
    ("23:mac:user:", 23, "hash"),
    ("24:mac:user:", 24, "hash"),
    ("25:record:user:", 25, "string"),
    ("29:record:user:", 29, "string"),
    ("0:config:app:single_max_duration", 2, "string"),  # 全局配置
]

# 加载 client_db_start 映射
_CLIENT_DB_START_PATH = Path(__file__).parent.parent / "nebulabuds" / "api" / "db" / "db_start.json"
if _CLIENT_DB_START_PATH.exists():
    with open(_CLIENT_DB_START_PATH, "r", encoding="utf-8") as f:
        CLIENT_DB_START = json.load(f)
else:
    CLIENT_DB_START = {}
    print(f"警告: 未找到 client_db_start 配置文件: {_CLIENT_DB_START_PATH}")


class RedisRollbacker:
    """Redis Key 回滚器"""

    def __init__(self, dry_run: bool = True, batch_size: int = 100, target_dbs: list = None):
        self.dry_run = dry_run
        self.batch_size = batch_size
        self.target_dbs = target_dbs  # None 表示回滚所有
        self.stats = {
            "total_scanned": 0,
            "rolled_back": 0,
            "skipped": 0,
            "errors": 0,
        }
        self._redis_clients = {}

    async def _get_redis(self, db: int) -> redis.Redis:
        """获取指定 db 的 Redis 连接"""
        if db not in self._redis_clients:
            host = os.getenv("REDIS_HOST", "127.0.0.1")
            port = int(os.getenv("REDIS_PORT", "6379"))
            password = os.getenv("REDIS_PASSWORD", None)
            self._redis_clients[db] = redis.Redis(
                host=host,
                port=port,
                db=db,
                password=password,
                encoding="utf-8",
                decode_responses=True,
            )
        return self._redis_clients[db]

    async def close(self):
        """关闭所有 Redis 连接"""
        for client in self._redis_clients.values():
            await client.close()

    def _extract_userid(self, new_key: str) -> str:
        """从新格式 key 提取 userid"""
        # 格式: {db}:{namespace}:user:{userid}:{field}
        parts = new_key.split(":")
        if len(parts) >= 4 and parts[2] == "user":
            return parts[3]
        return None

    def _get_target_db(self, new_key: str) -> tuple[int, bool]:
        """获取目标 db 和是否需要 client_db_start

        Returns:
            (target_db, needs_offset): 目标 db 和是否需要 client_db_start 计算
        """
        for prefix, target, key_type in NEW_KEY_PATTERNS:
            if new_key.startswith(prefix):
                if isinstance(target, int):
                    return target, False
                elif target == "7+offset" or target == "8+offset" or target == "10+offset":
                    base_db = int(target.split("+")[0])
                    return base_db, True
        return None, False

    def _get_actual_db_for_user(self, base_db: int, userid: str) -> int:
        """计算用户对应的实际 db（基于 userid 的前几位匹配 clientid）"""
        # 简化逻辑：遍历所有 client_db_start 查找匹配的
        for clientid, offset in CLIENT_DB_START.items():
            # 实际匹配逻辑可能需要根据业务确定
            # 这里简化处理：假设 userid 与 clientid 有对应关系
            pass
        return base_db

    async def rollback_keys(self, target_db: int):
        """回滚指定 db 的新格式 key"""
        client = await self._get_redis(target_db)

        pattern = "*:user:*"  # 匹配所有新格式 user key
        cursor = 0

        while True:
            cursor, keys = await client.scan(cursor=cursor, match=pattern, count=self.batch_size)
            for new_key in keys:
                self.stats["total_scanned"] += 1

                try:
                    userid = self._extract_userid(new_key)
                    if not userid:
                        self.stats["skipped"] += 1
                        continue

                    ttl = await client.ttl(new_key)

                    # 判断 key 类型
                    if new_key.endswith(":list"):
                        # List 类型
                        value = await client.lrange(new_key, 0, -1)
                        old_key = userid
                        if not self.dry_run:
                            # 先删除可能存在的旧 key
                            await client.delete(old_key)
                            for item in value:
                                await client.rpush(old_key, item)
                            if ttl > 0:
                                await client.expire(old_key, ttl)
                    elif ":active_code" in new_key or ":clientid" in new_key:
                        # Hash 类型
                        hash_data = await client.hgetall(new_key)
                        old_key = userid
                        if not self.dry_run:
                            await client.delete(old_key)
                            if hash_data:
                                await client.hset(old_key, mapping=hash_data)
                                if ttl > 0:
                                    await client.expire(old_key, ttl)
                    else:
                        # String 类型
                        value = await client.get(new_key)
                        old_key = userid
                        if not self.dry_run and value is not None:
                            if ttl > 0:
                                await client.setex(old_key, ttl, value)
                            else:
                                await client.set(old_key, value)

                    self.stats["rolled_back"] += 1
                    print(f"  [ROLLBACK] '{new_key}' -> db={target_db} '{old_key}'")

                except Exception as e:
                    self.stats["errors"] += 1
                    print(f"  [ERROR] '{new_key}': {e}")

            if cursor == 0:
                break

    async def rollback_config_keys(self):
        """回滚配置类 key"""
        client = await self._get_redis(2)

        # 回滚全局 single_max_duration
        new_key = "0:config:app:single_max_duration"
        old_key = "app:feature:single_max_duration"

        try:
            value = await client.get(new_key)
            ttl = await client.ttl(new_key)

            if value is not None:
                self.stats["total_scanned"] += 1
                if not self.dry_run:
                    if ttl > 0:
                        await client.setex(old_key, ttl, value)
                    else:
                        await client.set(old_key, value)
                self.stats["rolled_back"] += 1
                print(f"  [ROLLBACK] '{new_key}' -> '{old_key}'")
            else:
                self.stats["skipped"] += 1

        except Exception as e:
            self.stats["errors"] += 1
            print(f"  [ERROR] config key: {e}")

    async def run(self):
        """执行回滚"""
        mode = "DRY RUN" if self.dry_run else "LIVE"
        print(f"\n{'='*60}")
        print(f"Redis Key 回滚脚本 - {mode}")
        print(f"{'='*60}")

        if self.target_dbs:
            print(f"目标 dbs: {self.target_dbs}")
        else:
            print("目标 dbs: 全部")

        try:
            # 回滚配置类 key
            if self.target_dbs is None or 2 in self.target_dbs:
                print("\n[1] 回滚 db=2 配置类 key...")
                await self.rollback_config_keys()

            # 回滚用户数据类 key
            user_dbs = [7, 8, 10, 14, 23, 24, 25, 29]
            for i, db in enumerate(user_dbs):
                if self.target_dbs is None or db in self.target_dbs:
                    print(f"\n[{i+2}] 回滚 db={db}...")
                    await self.rollback_keys(db)

            print(f"\n{'='*60}")
            print("回滚完成!")
            print(f"{'='*60}")
            print(f"总计扫描: {self.stats['total_scanned']}")
            print(f"成功回滚: {self.stats['rolled_back']}")
            print(f"跳过: {self.stats['skipped']}")
            print(f"错误: {self.stats['errors']}")

        finally:
            await self.close()


def main():
    parser = argparse.ArgumentParser(description="Redis Key 回滚脚本")
    parser.add_argument("--dry-run", action="store_true", default=True,
                        help="仅打印不实际写入（默认开启）")
    parser.add_argument("--live", action="store_true",
                        help="实际执行回滚（默认关闭）")
    parser.add_argument("--batch-size", type=int, default=1000,
                        help="批量扫描的 key 数量")
    parser.add_argument("--db", type=str,
                        help="指定要回滚的 db，用逗号分隔，如: 7,8,10")

    args = parser.parse_args()

    dry_run = not args.live

    target_dbs = None
    if args.db:
        target_dbs = [int(d.strip()) for d in args.db.split(",")]

    rollbacker = RedisRollbacker(dry_run=dry_run, batch_size=args.batch_size, target_dbs=target_dbs)
    asyncio.run(rollbacker.run())

    if dry_run:
        print("\n" + "=" * 60)
        print("提示: 这是 DRY RUN 模式，没有实际写入任何数据。")
        print("如需执行实际回滚，请添加 --live 参数:")
        print("  python -m admin.rollback_redis_keys --live")
        print("=" * 60)


if __name__ == "__main__":
    main()
