import json
import asyncio
from sts.sts import Sts, Scope
from typing import Optional, Dict, List
from qcloud_cos import CosConfig, CosS3Client
from app.core.config import settings
from fastapi import Request
from app.common.utils.log_utils import log_util

logger = log_util.get_logger("cos_utils")


class CosUtils:
    FULL_COS_INFO = {
        "record.nebula-ai.net": {
            "TENCENT_REGION": "ap-shanghai",
            "BUCKET_ID": "voice-recorder-1325519451",
        },
        "hk-record.nebula-ai.net": {
            "TENCENT_REGION": "ap-shanghai",
            "BUCKET_ID": "voice-recorder-1325519451"
        },
        "mova.nebulabuds.com": {
            "TENCENT_REGION": "eu-frankfurt",
            "BUCKET_ID": "eu-voice-recorder-1325519451"
        },
        "recordtest.nebula-ai.net": {
            "TENCENT_REGION": "ap-shanghai",
            "BUCKET_ID": "voice-recorder-1325519451"
        },
        "na-record.nebula-ai.net": {
            "TENCENT_REGION": "na-siliconvalley",
            "BUCKET_ID": "na-recorder-1325519451"
        },
        "sg-record.nebula-ai.net": {
            "TENCENT_REGION": "ap-singapore",
            "BUCKET_ID": "sg-recorder-1325519451"
        },
    }

    def __init__(self, request: Request):
        self.secret_id = settings.tencent_secret_id
        self.secret_key = settings.tencent_secret_key
        self.bucket_id, self.region = self._get_cos_info(request)

    def _get_cos_info(self, request: Request):
        original_host = request.headers.get("x-forwarded-host")
        if not original_host:
            original_host = "hk-record.nebula-ai.net"
        cos_info = self.FULL_COS_INFO.get(original_host)
        bucket_id = cos_info.get("BUCKET_ID")
        region = cos_info.get("TENCENT_REGION")
        return bucket_id, region

    def _get_all_bucket_regions(self):
        seen = set()
        results = []
        for info in self.FULL_COS_INFO.values():
            bucket_id = info.get("BUCKET_ID")
            region = info.get("TENCENT_REGION")
            if not bucket_id or not region:
                continue
            key = (bucket_id, region)
            if key in seen:
                continue
            seen.add(key)
            results.append((bucket_id, region))
        return results

    def _build_upload_credential(
            self,
            bucket_id: str,
            region: str,
            prefixes: List[str],
            duration_seconds: int,
            ip_whitelist: Optional[list],
    ):
        if not bucket_id or not region:
            raise ValueError("bucket 或 region 为空，无法生成临时密钥")

        # COS 上传相关权限（仅上传相关动作）
        allow_actions = [
            "cos:PutObject",
            "cos:PostObject",
            "cos:InitiateMultipartUpload",
            "cos:ListMultipartUploads",
            "cos:ListParts",
            "cos:UploadPart",
            "cos:CompleteMultipartUpload",
        ]
        normalized_actions = []
        for action in allow_actions:
            if action.startswith("name/"):
                normalized_actions.append(action)
            else:
                normalized_actions.append(f"name/{action}")

        scopes = []
        for prefix in prefixes:
            scopes.append(Scope("name/cos:*", bucket_id, region, prefix))

        policy = Sts.get_policy(scopes)
        policy_dict = policy if isinstance(policy, dict) else json.loads(policy)
        for statement in policy_dict.get("statement", []):
            statement["action"] = normalized_actions

        # 如果 IP 白名单
        if ip_whitelist:
            for statement in policy_dict.get("statement", []):
                statement["condition"] = {"ip_equal": {"qcs:ip": ip_whitelist}}
        policy = policy_dict

        config = {
            "sts_scheme": "https",
            "sts_url": "sts.tencentcloudapi.com/",
            "duration_seconds": duration_seconds,
            "secret_id": self.secret_id,
            "secret_key": self.secret_key,
            "region": region,
            "policy": policy,
        }

        sts = Sts(config)
        response = sts.get_credential()
        result = dict(response)
        result["bucket"] = bucket_id
        result["region"] = region
        return result

    async def get_upload_credential(
            self,
            allow_prefix: Optional[list] = None,
            duration_seconds: int = 300,
            ip_whitelist: Optional[list] = None,
    ):
        def _build_and_request():
            if allow_prefix is None:
                prefixes = ["uploads/*"]
            elif isinstance(allow_prefix, str):
                prefixes = [allow_prefix]
            else:
                prefixes = allow_prefix
            return self._build_upload_credential(
                bucket_id=self.bucket_id,
                region=self.region,
                prefixes=prefixes,
                duration_seconds=duration_seconds,
                ip_whitelist=ip_whitelist,
            )

        try:
            return await asyncio.to_thread(_build_and_request)
        except Exception as e:
            logger.exception(f"获取临时密钥失败: {e}")
            return None

    async def get_multi_upload_credential(
            self,
            allow_prefix: Optional[list] = None,
            duration_seconds: int = 300,
            ip_whitelist: Optional[list] = None,
    ):
        def _build_and_request_all():
            if allow_prefix is None:
                prefixes = ["uploads/*"]
            elif isinstance(allow_prefix, str):
                prefixes = [allow_prefix]
            else:
                prefixes = allow_prefix

            results = []
            for bucket_id, region in self._get_all_bucket_regions():
                try:
                    results.append(self._build_upload_credential(
                        bucket_id=bucket_id,
                        region=region,
                        prefixes=prefixes,
                        duration_seconds=duration_seconds,
                        ip_whitelist=ip_whitelist,
                    ))
                except Exception as e:
                    logger.exception(f"获取临时密钥失败: {e}")
                    results.append({
                        "bucket": bucket_id,
                        "region": region,
                        "error": str(e),
                    })
            return results

        try:
            return await asyncio.to_thread(_build_and_request_all)
        except Exception as e:
            logger.exception(f"获取临时密钥失败: {e}")
            return None

    async def get_presigned_url(
            self,
            keys: List[str],
            expires: int = 43200,
    ):
        def _build_urls():
            if not self.bucket_id or not self.region or not keys:
                logger.error("生成预签名 URL 失败: bucket/region/key 不能为空")
                return None

            if not isinstance(keys, list):
                logger.error("生成预签名 URL 失败: key 必须为列表")
                return None

            params = {"response-content-disposition": "attachment"}
            config = CosConfig(
                Region=self.region,
                SecretId=self.secret_id,
                SecretKey=self.secret_key,
                Scheme="https",
            )
            client = CosS3Client(config)

            kwargs = {
                "Bucket": self.bucket_id,
                "Expired": expires,
                "SignHost": False,
            }
            if params:
                kwargs["Params"] = params

            urls = []
            for item in keys:
                if not item:
                    urls.append(None)
                    continue
                kwargs["Key"] = item
                if hasattr(client, "get_presigned_download_url"):
                    urls.append(client.get_presigned_download_url(**kwargs))
                else:
                    urls.append(client.get_presigned_url(Method="GET", **kwargs))
            return urls

        try:
            return await asyncio.to_thread(_build_urls)
        except Exception as e:
            logger.exception(f"生成预签名 URL 失败: {e}")
            return None

# if __name__ == "__main__":
#     class _DummyRequest:
#         def __init__(self, host: str):
#             self.headers = {"x-forwarded-host": host}
#
#
#     req = _DummyRequest("hk-record.nebula-ai.net")
#     cos_utils = CosUtils(req)
#
#
#     async def _run():
#         # credential = await cos_utils.get_upload_credential(
#         #     allow_prefix=["uploads/*"],
#         #     duration_seconds=300,
#         #     ip_whitelist=None,
#         # )
#         # print(json.dumps(credential, indent=4))
#
#         urls = await cos_utils.get_presigned_url(
#             keys=["/firmware/3085_56.bin", "audio/897007169.mp3"],
#         )
#         print(json.dumps(urls, indent=4))
#
#
#     asyncio.run(_run())
