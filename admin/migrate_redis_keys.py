"""
Redis Key 迁移脚本：将旧系统多 db 分片格式迁移到新统一 key 格式。

旧格式（db 分片）：
  db=RECORD_DUREATION_DB + client_db_start[clientid] -> key=userid
  db=MUSIC_NUM_DB + client_db_start[clientid] -> key=userid
  db=AI_NUM_DB + client_db_start[clientid] -> key=userid
  db=USER_BTNAME_DB -> key=userid (List)
  db=USER_MAC_ACTIVE_CODE -> key=userid (Hash)
  db=USER_MAC_CLIENTID -> key=userid (Hash)
  db=ONE_YEAR_NO_DEDUCTION_RECORDING_DB -> key=userid
  db=RECORD_REST_DB -> key=userid
  db=CONFIG_DB -> key="app:feature:single_max_duration" 或 "app:feature:single_max_duration:{clientid}"

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

用法：
  python -m admin.migrate_redis_keys --dry-run
  python -m admin.migrate_redis_keys --batch-size 1000
  python -m admin.migrate_redis_keys --start-userid 10000000 --end-userid 20000000
"""

import argparse
import asyncio
import json
import os
import sys
from pathlib import Path

# 添加项目根目录到 path
sys.path.insert(0, str(Path(__file__).parent.parent))

import redis.asyncio as redis
from dotenv import load_dotenv

load_dotenv()

# ==================== 旧系统常量 ====================
RECORD_DUREATION_DB = 7
MUSIC_NUM_DB = 10
AI_NUM_DB = 8
USER_BTNAME_DB = 14
USER_MAC_ACTIVE_CODE = 23
USER_MAC_CLIENTID = 24
ONE_YEAR_NO_DEDUCTION_RECORDING_DB = 25
RECORD_REST_DB = 29
CONFIG_DB = 2

# 加载 client_db_start 映射
_CLIENT_DB_START_PATH = Path(__file__).parent.parent / "nebulabuds" / "api" / "db" / "db_start.json"
if _CLIENT_DB_START_PATH.exists():
    with open(_CLIENT_DB_START_PATH, "r", encoding="utf-8") as f:
        CLIENT_DB_START = json.load(f)
else:
    CLIENT_DB_START = {}
    print(f"警告: 未找到 client_db_start 配置文件: {_CLIENT_DB_START_PATH}")

# 固定偏移（不需要 client_db_start 计算的 db）
FIXED_OFFSET_MAP = {
    USER_BTNAME_DB: "14:btname:user:{userid}:list",
    USER_MAC_ACTIVE_CODE: "23:mac:user:{userid}:active_code",
    USER_MAC_CLIENTID: "24:mac:user:{userid}:clientid",
    ONE_YEAR_NO_DEDUCTION_RECORDING_DB: "25:record:user:{userid}:free_date",
    RECORD_REST_DB: "29:record:user:{userid}:rest",
}

# 分片偏移（需要 client_db_start 计算实际 db）
SHARDED_DB_TYPES = {
    RECORD_DUREATION_DB: ("7:record:user:{userid}:duration", "record_duration"),
    MUSIC_NUM_DB: ("10:music:user:{userid}:num", "music_num"),
    AI_NUM_DB: ("8:ai:user:{userid}:num", "ai_num"),
}

# 配置类 key（存储在 db=2）
CONFIG_KEYS = {
    "app:feature:single_max_duration": "0:config:app:single_max_duration",
}


class RedisMigrator:
    """Redis Key 迁移器"""

    def __init__(self, dry_run: bool = True, batch_size: int = 100):
        self.dry_run = dry_run
        self.batch_size = batch_size
        self.stats = {
            "total_scanned": 0,
            "migrated": 0,
            "skipped": 0,
            "errors": 0,
            "by_type": {},
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

    def _get_actual_db(self, base_db: int, clientid: str = None) -> int:
        """计算实际 db 编号"""
        if clientid and clientid in CLIENT_DB_START:
            return base_db + CLIENT_DB_START[clientid]
        return base_db

    async def migrate_fixed_db(self, base_db: int, new_key_template: str, key_type: str):
        """迁移固定偏移的 db 数据"""
        client = await self._get_redis(base_db)
        pattern = "*"  # 匹配所有 key

        cursor = 0
        while True:
            cursor, keys = await client.scan(cursor=cursor, match=pattern, count=self.batch_size)
            for old_key in keys:
                self.stats["total_scanned"] += 1

                try:
                    # 解析 old_key 获取 userid
                    userid = old_key

                    # 根据 key 类型获取值
                    if key_type == "list":
                        value = await client.lrange(old_key, 0, -1)
                        ttl = await client.ttl(old_key)
                        new_key = new_key_template.format(userid=userid)
                        if not self.dry_run:
                            if ttl > 0:
                                await client.delete(new_key)
                            for item in value:
                                await client.rpush(new_key, item)
                            if ttl > 0:
                                await client.expire(new_key, ttl)
                    else:
                        value = await client.get(old_key)
                        ttl = await client.ttl(old_key)
                        new_key = new_key_template.format(userid=userid)
                        if not self.dry_run:
                            if value is not None:
                                if ttl > 0:
                                    await client.setex(new_key, ttl, value)
                                else:
                                    await client.set(new_key, value)

                    self.stats["migrated"] += 1
                    self.stats["by_type"][key_type] = self.stats["by_type"].get(key_type, 0) + 1
                    print(f"  [MIGRATE] db={base_db} '{old_key}' -> '{new_key}'")

                except Exception as e:
                    self.stats["errors"] += 1
                    print(f"  [ERROR] db={base_db} '{old_key}': {e}")

            if cursor == 0:
                break

    async def migrate_hash_db(self, base_db: int, new_key_template: str):
        """迁移 Hash 类型数据"""
        client = await self._get_redis(base_db)

        cursor = 0
        while True:
            cursor, keys = await client.scan(cursor=cursor, match="*", count=self.batch_size)
            for old_key in keys:
                self.stats["total_scanned"] += 1

                try:
                    userid = old_key
                    ttl = await client.ttl(old_key)

                    # 获取所有 field-value
                    hash_data = await client.hgetall(old_key)
                    new_key = new_key_template.format(userid=userid)

                    if not self.dry_run:
                        if hash_data:
                            await client.delete(new_key)
                            await client.hset(new_key, mapping=hash_data)
                            if ttl > 0:
                                await client.expire(new_key, ttl)

                    self.stats["migrated"] += 1
                    self.stats["by_type"]["hash"] = self.stats["by_type"].get("hash", 0) + 1
                    print(f"  [MIGRATE] db={base_db} '{old_key}' (Hash, {len(hash_data)} fields) -> '{new_key}'")

                except Exception as e:
                    self.stats["errors"] += 1
                    print(f"  [ERROR] db={base_db} '{old_key}': {e}")

            if cursor == 0:
                break

    async def migrate_config_db(self):
        """迁移配置类 key（db=2）"""
        client = await self._get_redis(CONFIG_DB)

        for old_key, new_key in CONFIG_KEYS.items():
            try:
                value = await client.get(old_key)
                ttl = await client.ttl(old_key)

                if value is not None:
                    self.stats["total_scanned"] += 1
                    if not self.dry_run:
                        if ttl > 0:
                            await client.setex(new_key, ttl, value)
                        else:
                            await client.set(new_key, value)
                    self.stats["migrated"] += 1
                    print(f"  [MIGRATE] db={CONFIG_DB} '{old_key}' -> '{new_key}'")
                else:
                    self.stats["skipped"] += 1

            except Exception as e:
                self.stats["errors"] += 1
                print(f"  [ERROR] db={CONFIG_DB} '{old_key}': {e}")

    async def migrate_by_userid_range(self, start_userid: int, end_userid: int):
        """按 userid 范围迁移（适用于分片数据）"""
        for clientid, db_offset in CLIENT_DB_START.items():
            for base_db, (new_key_template, key_type) in SHARDED_DB_TYPES.items():
                actual_db = base_db + db_offset
                client = await self._get_redis(actual_db)

                for userid in range(start_userid, end_userid + 1):
                    userid_str = str(userid)
                    self.stats["total_scanned"] += 1

                    try:
                        if key_type == "list":
                            value = await client.lrange(userid_str, 0, -1)
                            ttl = await client.ttl(userid_str)
                            new_key = new_key_template.format(userid=userid_str)
                            if value or ttl > 0:
                                if not self.dry_run:
                                    if ttl > 0:
                                        await client.delete(new_key)
                                    for item in value:
                                        await client.rpush(new_key, item)
                                    if ttl > 0:
                                        await client.expire(new_key, ttl)
                                self.stats["migrated"] += 1
                                self.stats["by_type"][key_type] = self.stats["by_type"].get(key_type, 0) + 1
                                print(f"  [MIGRATE] db={actual_db} '{userid_str}' -> '{new_key}'")
                            else:
                                self.stats["skipped"] += 1
                        else:
                            value = await client.get(userid_str)
                            ttl = await client.ttl(userid_str)
                            new_key = new_key_template.format(userid=userid_str)
                            if value is not None:
                                if not self.dry_run:
                                    if ttl > 0:
                                        await client.setex(new_key, ttl, value)
                                    else:
                                        await client.set(new_key, value)
                                self.stats["migrated"] += 1
                                self.stats["by_type"][key_type] = self.stats["by_type"].get(key_type, 0) + 1
                                print(f"  [MIGRATE] db={actual_db} '{userid_str}' -> '{new_key}'")
                            else:
                                self.stats["skipped"] += 1

                    except Exception as e:
                        self.stats["errors"] += 1
                        print(f"  [ERROR] db={actual_db} '{userid_str}': {e}")

    async def run(self, userid_start: int = None, userid_end: int = None):
        """执行迁移"""
        mode = "DRY RUN" if self.dry_run else "LIVE"
        print(f"\n{'='*60}")
        print(f"Redis Key 迁移脚本 - {mode}")
        print(f"{'='*60}")
        print(f"Batch size: {self.batch_size}")
        if userid_start and userid_end:
            print(f"UserID 范围: {userid_start} - {userid_end}")
            print(f"注意: 将只迁移该范围内的分片数据")

        try:
            # 迁移固定偏移的 db
            print("\n[1/6] 迁移 db=14 (USER_BTNAME_DB)...")
            await self.migrate_fixed_db(USER_BTNAME_DB, FIXED_OFFSET_MAP[USER_BTNAME_DB], "list")

            print("\n[2/6] 迁移 db=23 (USER_MAC_ACTIVE_CODE)...")
            await self.migrate_hash_db(USER_MAC_ACTIVE_CODE, FIXED_OFFSET_MAP[USER_MAC_ACTIVE_CODE])

            print("\n[3/6] 迁移 db=24 (USER_MAC_CLIENTID)...")
            await self.migrate_hash_db(USER_MAC_CLIENTID, FIXED_OFFSET_MAP[USER_MAC_CLIENTID])

            print("\n[4/6] 迁移 db=25 (ONE_YEAR_NO_DEDUCTION_RECORDING_DB)...")
            await self.migrate_fixed_db(ONE_YEAR_NO_DEDUCTION_RECORDING_DB, FIXED_OFFSET_MAP[ONE_YEAR_NO_DEDUCTION_RECORDING_DB], "string")

            print("\n[5/6] 迁移 db=29 (RECORD_REST_DB)...")
            await self.migrate_fixed_db(RECORD_REST_DB, FIXED_OFFSET_MAP[RECORD_REST_DB], "string")

            print("\n[6/6] 迁移 db=2 配置类 key...")
            await self.migrate_config_db()

            # 如果指定了 userid 范围，迁移分片数据
            if userid_start and userid_end:
                print(f"\n[额外] 迁移分片数据 (db=7,8,10)...")
                print(f"  ClientID 数量: {len(CLIENT_DB_START)}")
                estimated = len(CLIENT_DB_START) * (userid_end - userid_start + 1) * 3
                print(f"  预计迁移 key 数量: ~{estimated} (可能略少，因为部分 key 可能不存在)")
                await self.migrate_by_userid_range(userid_start, userid_end)

            print(f"\n{'='*60}")
            print("迁移完成!")
            print(f"{'='*60}")
            print(f"总计扫描: {self.stats['total_scanned']}")
            print(f"成功迁移: {self.stats['migrated']}")
            print(f"跳过(无数据): {self.stats['skipped']}")
            print(f"错误: {self.stats['errors']}")
            print(f"\n按类型统计:")
            for key_type, count in self.stats["by_type"].items():
                print(f"  {key_type}: {count}")

        finally:
            await self.close()


def main():
    parser = argparse.ArgumentParser(description="Redis Key 迁移脚本")
    parser.add_argument("--dry-run", action="store_true", default=True,
                        help="仅打印不实际写入（默认开启）")
    parser.add_argument("--live", action="store_true",
                        help="实际执行迁移（默认关闭）")
    parser.add_argument("--batch-size", type=int, default=1000,
                        help="批量扫描的 key 数量")
    parser.add_argument("--start-userid", type=int,
                        help="起始 userid（分片数据迁移）")
    parser.add_argument("--end-userid", type=int,
                        help="结束 userid（分片数据迁移）")

    args = parser.parse_args()

    # --live 覆盖 --dry-run
    dry_run = not args.live

    migrator = RedisMigrator(dry_run=dry_run, batch_size=args.batch_size)

    if args.start_userid and args.end_userid:
        asyncio.run(migrator.run(args.start_userid, args.end_userid))
    else:
        asyncio.run(migrator.run())

    # 如果是 dry run，提示用户
    if dry_run:
        print("\n" + "=" * 60)
        print("提示: 这是 DRY RUN 模式，没有实际写入任何数据。")
        print("如需执行实际迁移，请添加 --live 参数:")
        print("  python -m admin.migrate_redis_keys --live")
        print("=" * 60)


if __name__ == "__main__":
    main()
