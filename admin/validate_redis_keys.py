"""
Redis Key 数据校验脚本：抽样比对新旧 key 的值，确保迁移正确。

用法：
  python -m admin.validate_redis_keys --sample-size 100
  python -m admin.validate_redis_keys --userid-start 10000000 --userid-end 20000000
  python -m admin.validate_redis_keys --db 7 --dry-run
"""

import argparse
import asyncio
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import redis.asyncio as redis
from dotenv import load_dotenv

load_dotenv()

# ==================== 常量 ====================
RECORD_DUREATION_DB = 7
MUSIC_NUM_DB = 10
AI_NUM_DB = 8
USER_BTNAME_DB = 14
USER_MAC_ACTIVE_CODE = 23
USER_MAC_CLIENTID = 24
ONE_YEAR_NO_DEDUCTION_RECORDING_DB = 25
RECORD_REST_DB = 29
CONFIG_DB = 2

# 新 key 前缀到旧 db 的映射
NEW_PREFIX_TO_OLD_DB = {
    "7:record:user:": (RECORD_DUREATION_DB, "string"),
    "8:ai:user:": (AI_NUM_DB, "string"),
    "10:music:user:": (MUSIC_NUM_DB, "string"),
    "14:btname:user:": (USER_BTNAME_DB, "list"),
    "23:mac:user:": (USER_MAC_ACTIVE_CODE, "hash"),
    "24:mac:user:": (USER_MAC_CLIENTID, "hash"),
    "25:record:user:": (ONE_YEAR_NO_DEDUCTION_RECORDING_DB, "string"),
    "29:record:user:": (RECORD_REST_DB, "string"),
}

# 加载 client_db_start 映射
_CLIENT_DB_START_PATH = Path(__file__).parent.parent / "nebulabuds" / "api" / "db" / "db_start.json"
if _CLIENT_DB_START_PATH.exists():
    with open(_CLIENT_DB_START_PATH, "r", encoding="utf-8") as f:
        CLIENT_DB_START = json.load(f)
else:
    CLIENT_DB_START = {}
    print(f"警告: 未找到 client_db_start 配置文件: {_CLIENT_DB_START_PATH}")


class RedisValidator:
    """Redis 数据校验器"""

    def __init__(
        self,
        sample_size: int = 100,
        userid_start: int = None,
        userid_end: int = None,
        target_db: int = None,
    ):
        self.sample_size = sample_size
        self.userid_start = userid_start
        self.userid_end = userid_end
        self.target_db = target_db
        self.stats = {
            "compared": 0,
            "matched": 0,
            "mismatched": 0,
            "missing_old": 0,
            "missing_new": 0,
            "errors": 0,
            "details": [],
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
        parts = new_key.split(":")
        if len(parts) >= 4 and parts[2] == "user":
            return parts[3]
        return None

    async def _get_old_db_for_user(self, base_db: int, userid: int) -> int:
        """获取用户对应的实际旧 db（分片）"""
        # 这里需要业务逻辑来确定 userid 对应的 clientid
        # 简化处理：假设 base_db + 某个固定偏移
        # 实际使用时需要根据业务调整
        return base_db

    async def compare_string_keys(
        self,
        new_key: str,
        old_db: int,
        userid: int,
        actual_old_db: int,
    ):
        """比较 String 类型 key"""
        new_client = await self._get_redis(new_db := self._parse_db(new_key))
        old_client = await self._get_redis(actual_old_db)

        new_value = await new_client.get(new_key)
        old_value = await old_client.get(userid)

        self.stats["compared"] += 1

        if new_value is None and old_value is None:
            self.stats["matched"] += 1
            return True
        elif new_value == old_value:
            self.stats["matched"] += 1
            return True
        elif new_value is None:
            self.stats["missing_new"] += 1
            self.stats["details"].append({
                "type": "string",
                "new_key": new_key,
                "old_db": actual_old_db,
                "old_key": userid,
                "old_value": old_value,
                "new_value": None,
                "status": "missing_new",
            })
            return False
        elif old_value is None:
            self.stats["missing_old"] += 1
            self.stats["details"].append({
                "type": "string",
                "new_key": new_key,
                "old_db": actual_old_db,
                "old_key": userid,
                "new_value": new_value,
                "old_value": None,
                "status": "missing_old",
            })
            return False
        else:
            self.stats["mismatched"] += 1
            self.stats["details"].append({
                "type": "string",
                "new_key": new_key,
                "old_db": actual_old_db,
                "old_key": userid,
                "new_value": new_value,
                "old_value": old_value,
                "status": "mismatch",
            })
            return False

    async def compare_list_keys(self, new_key: str, old_db: int, userid: int):
        """比较 List 类型 key"""
        new_client = await self._get_redis(self._parse_db(new_key))
        old_client = await self._get_redis(old_db)

        new_value = await new_client.lrange(new_key, 0, -1)
        old_value = await old_client.lrange(userid, 0, -1)

        self.stats["compared"] += 1

        if set(new_value) == set(old_value):
            self.stats["matched"] += 1
            return True
        else:
            self.stats["mismatched"] += 1
            self.stats["details"].append({
                "type": "list",
                "new_key": new_key,
                "old_db": old_db,
                "old_key": userid,
                "new_value": new_value,
                "old_value": old_value,
                "status": "mismatch",
            })
            return False

    async def compare_hash_keys(
        self,
        new_key: str,
        old_db: int,
        userid: int,
    ):
        """比较 Hash 类型 key"""
        new_client = await self._get_redis(self._parse_db(new_key))
        old_client = await self._get_redis(old_db)

        new_value = await new_client.hgetall(new_key)
        old_value = await old_client.hgetall(userid)

        self.stats["compared"] += 1

        if new_value == old_value:
            self.stats["matched"] += 1
            return True
        else:
            self.stats["mismatched"] += 1
            self.stats["details"].append({
                "type": "hash",
                "new_key": new_key,
                "old_db": old_db,
                "old_key": userid,
                "new_value": new_value,
                "old_value": old_value,
                "status": "mismatch",
            })
            return False

    def _parse_db(self, new_key: str) -> int:
        """从新 key 解析 db 编号"""
        try:
            return int(new_key.split(":")[0])
        except (ValueError, IndexError):
            return 0

    async def validate_db(self, new_prefix: str, old_db: int, key_type: str):
        """校验指定类型的 key"""
        target_new_db = self._parse_db(new_prefix)
        new_client = await self._get_redis(target_new_db)

        pattern = f"{new_prefix}*"
        cursor = 0
        validated = 0

        print(f"\n  校验 {new_prefix}* (db={target_new_db}, type={key_type})...")

        while cursor != -1 and validated < self.sample_size:
            cursor, keys = await new_client.scan(cursor=cursor if cursor > 0 else 0, match=pattern, count=100)

            for new_key in keys:
                if validated >= self.sample_size:
                    break

                userid = self._extract_userid(new_key)
                if not userid:
                    continue

                try:
                    if key_type == "string":
                        await self.compare_string_keys(new_key, old_db, userid, old_db)
                    elif key_type == "list":
                        await self.compare_list_keys(new_key, old_db, userid)
                    elif key_type == "hash":
                        await self.compare_hash_keys(new_key, old_db, userid)
                    validated += 1

                    if validated % 10 == 0:
                        print(f"    已校验: {validated}/{self.sample_size}...")

                except Exception as e:
                    self.stats["errors"] += 1
                    print(f"    [ERROR] {new_key}: {e}")

            if cursor == 0:
                break

        print(f"    完成: 校验了 {validated} 个 key")

    async def validate_config_keys(self):
        """校验配置类 key"""
        new_client = await self._get_redis(0)
        old_client = await self._get_redis(CONFIG_DB)

        new_key = "0:config:app:single_max_duration"
        old_key = "app:feature:single_max_duration"

        new_value = await new_client.get(new_key)
        old_value = await old_client.get(old_key)

        self.stats["compared"] += 1

        if new_value == old_value:
            self.stats["matched"] += 1
            print(f"\n  [MATCH] config key: '{new_key}' == '{old_key}'")
        else:
            self.stats["mismatched"] += 1
            print(f"\n  [MISMATCH] config key:")
            print(f"    new: '{new_key}' = {new_value}")
            print(f"    old: '{old_key}' = {old_value}")

    async def run(self):
        """执行校验"""
        print(f"\n{'='*60}")
        print("Redis 数据校验脚本")
        print(f"{'='*60}")
        print(f"采样数量: {self.sample_size}")
        if self.target_db:
            print(f"目标 db: {self.target_db}")
        if self.userid_start and self.userid_end:
            print(f"UserID 范围: {self.userid_start} - {self.userid_end}")

        try:
            # 校验配置类 key
            print("\n[1] 校验 db=0/2 配置类 key...")
            await self.validate_config_keys()

            # 校验用户数据类 key
            db_map = [
                ("7:record:user:", RECORD_DUREATION_DB, "string"),
                ("8:ai:user:", AI_NUM_DB, "string"),
                ("10:music:user:", MUSIC_NUM_DB, "string"),
                ("14:btname:user:", USER_BTNAME_DB, "list"),
                ("23:mac:user:", USER_MAC_ACTIVE_CODE, "hash"),
                ("24:mac:user:", USER_MAC_CLIENTID, "hash"),
                ("25:record:user:", ONE_YEAR_NO_DEDUCTION_RECORDING_DB, "string"),
                ("29:record:user:", RECORD_REST_DB, "string"),
            ]

            for i, (prefix, old_db, key_type) in enumerate(db_map):
                if self.target_db is None or old_db == self.target_db:
                    print(f"\n[{i+2}] 校验 db={old_db}...")
                    await self.validate_db(prefix, old_db, key_type)

            print(f"\n{'='*60}")
            print("校验完成!")
            print(f"{'='*60}")
            print(f"总计比较: {self.stats['compared']}")
            print(f"匹配: {self.stats['matched']}")
            print(f"不匹配: {self.stats['mismatched']}")
            print(f"新 key 缺失: {self.stats['missing_new']}")
            print(f"旧 key 缺失: {self.stats['missing_old']}")
            print(f"错误: {self.stats['errors']}")

            # 输出不匹配详情
            if self.stats["details"] and len(self.stats["details"]) <= 20:
                print(f"\n不匹配详情:")
                for detail in self.stats["details"]:
                    print(f"  - {detail['status']}: {detail['new_key']} vs {detail.get('old_db', '?')}/{detail.get('old_key', '?')}")
            elif self.stats["details"]:
                print(f"\n不匹配详情 (前 20 条):")
                for detail in self.stats["details"][:20]:
                    print(f"  - {detail['status']}: {detail['new_key']} vs {detail.get('old_db', '?')}/{detail.get('old_key', '?')}")
                print(f"  ... 共 {len(self.stats['details'])} 条")

        finally:
            await self.close()


def main():
    parser = argparse.ArgumentParser(description="Redis 数据校验脚本")
    parser.add_argument("--sample-size", type=int, default=100,
                        help="每个类型抽样的 key 数量")
    parser.add_argument("--userid-start", type=int,
                        help="起始 userid")
    parser.add_argument("--userid-end", type=int,
                        help="结束 userid")
    parser.add_argument("--db", type=int,
                        help="指定要校验的 db")

    args = parser.parse_args()

    validator = RedisValidator(
        sample_size=args.sample_size,
        userid_start=args.userid_start,
        userid_end=args.userid_end,
        target_db=args.db,
    )
    asyncio.run(validator.run())


if __name__ == "__main__":
    main()
