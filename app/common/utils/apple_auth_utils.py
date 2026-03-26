import time
from typing import Any, Dict, Optional

import httpx
import jwt
from jwt import PyJWTError

from app.common.utils.log_utils import log_util

logger = log_util.get_logger("apple_auth")

_JWKS_CACHE: Dict[str, Any] = {"keys": [], "expires_at": 0}
_JWKS_CACHE_TTL_SECONDS = 3600


async def _fetch_jwks(jwks_url: str) -> Optional[Dict[str, Any]]:
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(jwks_url)
            response.raise_for_status()
            return response.json()
    except Exception as exc:
        logger.error(f"Apple JWKS 获取失败: {exc}")
        return None


async def _get_cached_jwks(jwks_url: str) -> Optional[Dict[str, Any]]:
    now = time.time()
    if _JWKS_CACHE["keys"] and now < _JWKS_CACHE["expires_at"]:
        return {"keys": _JWKS_CACHE["keys"]}

    jwks = await _fetch_jwks(jwks_url)
    if jwks and "keys" in jwks:
        _JWKS_CACHE["keys"] = jwks["keys"]
        _JWKS_CACHE["expires_at"] = now + _JWKS_CACHE_TTL_SECONDS
        return jwks

    return None


def _find_jwk(keys: list, kid: str) -> Optional[Dict[str, Any]]:
    for key in keys:
        if key.get("kid") == kid:
            return key
    return None


async def verify_apple_id_token(
    id_token: str,
    *,
    client_id: str,
    issuer: str,
    jwks_url: str,
) -> Optional[Dict[str, Any]]:
    try:
        header = jwt.get_unverified_header(id_token)
        kid = header.get("kid")
        alg = header.get("alg")
        if not kid or not alg:
            logger.warning("Apple id_token header 缺少 kid/alg")
            return None

        jwks = await _get_cached_jwks(jwks_url)
        if not jwks:
            return None

        jwk = _find_jwk(jwks.get("keys", []), kid)
        if not jwk:
            logger.warning("Apple JWKS 未找到匹配的 kid")
            return None

        public_key = jwt.algorithms.RSAAlgorithm.from_jwk(jwk)
        payload = jwt.decode(
            id_token,
            public_key,
            algorithms=[alg],
            audience=client_id,
            issuer=issuer,
        )
        return payload
    except PyJWTError as exc:
        logger.warning(f"Apple id_token 校验失败: {exc}")
        return None
    except Exception as exc:
        logger.error(f"Apple id_token 校验异常: {exc}")
        return None
