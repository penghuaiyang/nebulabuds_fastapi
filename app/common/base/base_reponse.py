import hashlib
from typing import Optional

from fastapi import Request
from starlette.responses import JSONResponse

from app.common.llm.translate import translate_text
from app.common.utils.log_utils import log_util
from app.db.redis import get_redis_client
from app.models.models import TranslationCache

logger = log_util.get_logger("api_response")

CHINESE_LANG_CODES = {
    "zh", "zh-cn", "zh-hans", "zh-hant", "zh-sg", "zh-tw", "zh-hk", "cn"
}


def _text_hash(source_text: str) -> str:
    return hashlib.sha256(source_text.encode("utf-8")).hexdigest()


def _cache_key(target_language: str, text_hash: str) -> str:
    return f"translation:{target_language}:{text_hash}"


async def _get_cached_translation(source_text: str, target_language: str, redis_client=None) -> Optional[str]:
    text_hash = _text_hash(source_text)
    key = _cache_key(target_language, text_hash)

    if redis_client is not None:
        try:
            cached = await redis_client.get(key)
            if cached:
                return cached
        except Exception as exc:  # pragma: no cover - defensive log
            logger.warning(f"Redis translation lookup failed: {exc}")

    try:
        record = await TranslationCache.get_or_none(source_hash=text_hash, target_language=target_language)
        if record and record.source_text == source_text:
            if redis_client is not None:
                try:
                    await redis_client.set(key, record.translated_text,ex=10)
                except Exception as exc:  # pragma: no cover - defensive log
                    logger.warning(f"Redis translation backfill failed: {exc}")
            return record.translated_text
    except Exception as exc:  # pragma: no cover - defensive log
        logger.error(f"Database translation lookup failed: {exc}")

    return None


async def _store_translation(source_text: str, target_language: str, translated_text: str, redis_client=None) -> None:
    text_hash = _text_hash(source_text)
    key = _cache_key(target_language, text_hash)

    if redis_client is not None:
        try:
            await redis_client.set(key, translated_text,ex=10)
        except Exception as exc:  # pragma: no cover - defensive log
            logger.warning(f"Redis translation save failed: {exc}")

    try:
        record = await TranslationCache.get_or_none(source_hash=text_hash, target_language=target_language)
        if record:
            record.source_text = source_text
            record.translated_text = translated_text
            await record.save()
        else:
            await TranslationCache.create(
                source_text=source_text,
                source_hash=text_hash,
                target_language=target_language,
                translated_text=translated_text,
            )
    except Exception as exc:  # pragma: no cover - defensive log
        logger.error(f"Database translation save failed: {exc}")


async def _translate_message(message: str, target_language: str) -> str:
    """Translate message using cache, DB, and translate_text helper."""

    normalized_lang = target_language.strip().lower().replace("_", "-")
    if not normalized_lang:
        return message

    if normalized_lang in CHINESE_LANG_CODES or normalized_lang.startswith("zh"):
        return message

    redis_client = await get_redis_client()

    cached = await _get_cached_translation(message, normalized_lang, redis_client)
    if cached is not None:
        return cached

    translated = await translate_text(source_text=message, target_language=normalized_lang)
    if translated:
        await _store_translation(message, normalized_lang, translated, redis_client)
        return translated

    return message


async def api_write(code=1, message="ok", request: Optional[Request] = None, **kwargs):
    target_language = None
    if request is not None:
        target_language = request.headers.get("X-Client-Lang")

    translated_message = message
    if message and target_language:
        translated_message = await _translate_message(str(message), target_language)

    if "data" not in kwargs:
        response = {
            "code": code,
            "message": translated_message,
            "data": kwargs
        }
    else:
        response = {
            "code": code,
            "message": translated_message,
            "data": kwargs["data"]
        }
    return JSONResponse(content=response)
