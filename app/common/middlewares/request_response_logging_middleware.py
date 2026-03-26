import json
import time
from urllib.parse import parse_qs

from app.common.utils.log_utils import log_util

logger = log_util.get_logger("request_response")

TOKEN_REDACTED = "[REDACTED]"
BINARY_OMITTED = "[BINARY OMITTED]"
BINARY_CONTENT_PREFIXES = (
    "application/octet-stream",
    "application/pdf",
    "application/zip",
    "application/x-7z-compressed",
    "application/x-rar-compressed",
    "image/",
    "audio/",
    "video/",
    "multipart/form-data",
)


def _is_binary_content_type(content_type: str) -> bool:
    if not content_type:
        return False
    normalized = content_type.split(";", 1)[0].strip().lower()
    for prefix in BINARY_CONTENT_PREFIXES:
        if normalized.startswith(prefix):
            return True
    return False


def _headers_to_dict(headers) -> dict:
    result = {}
    for key, value in headers:
        header_key = key.decode("latin1") if isinstance(key, (bytes, bytearray)) else str(key)
        header_value = value.decode("latin1") if isinstance(value, (bytes, bytearray)) else str(value)
        lowered = header_key.lower()
        if lowered in result:
            existing = result[lowered]
            if isinstance(existing, list):
                existing.append(header_value)
            else:
                result[lowered] = [existing, header_value]
        else:
            result[lowered] = header_value
    return result


def _redact_headers(headers: dict) -> dict:
    redacted = {}
    for key, value in headers.items():
        lowered = str(key).lower()
        if "authorization" in lowered or "token" in lowered:
            redacted[key] = TOKEN_REDACTED
        else:
            redacted[key] = value
    return redacted


def _redact_tokens(data):
    if isinstance(data, dict):
        sanitized = {}
        for key, value in data.items():
            if "token" in str(key).lower():
                sanitized[key] = TOKEN_REDACTED
            else:
                sanitized[key] = _redact_tokens(value)
        return sanitized
    if isinstance(data, list):
        return [_redact_tokens(item) for item in data]
    return data


def _decode_body(body_bytes: bytes, content_type: str):
    if not body_bytes:
        return ""
    if _is_binary_content_type(content_type):
        return BINARY_OMITTED
    try:
        text = body_bytes.decode("utf-8")
    except UnicodeDecodeError:
        return BINARY_OMITTED
    lowered = (content_type or "").lower()
    if "application/json" in lowered:
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return text
    if "application/x-www-form-urlencoded" in lowered:
        parsed = parse_qs(text, keep_blank_values=True)
        return {key: values[0] if len(values) == 1 else values for key, values in parsed.items()}
    return text


def _get_client_ip(scope) -> str:
    client = scope.get("client")
    if not client:
        return "unknown"
    return client[0] or "unknown"


def _pretty(value) -> str:
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False, indent=2)
    return json.dumps(value, ensure_ascii=False)


def _indent(text: str, prefix: str = "  ") -> str:
    if not text:
        return prefix
    return "\n".join(f"{prefix}{line}" for line in text.splitlines())


class RequestResponseLoggingMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope.get("type") != "http":
            await self.app(scope, receive, send)
            return

        start_time = time.perf_counter()
        request_headers = _headers_to_dict(scope.get("headers", []))
        request_content_type = request_headers.get("content-type", "")
        request_is_binary = _is_binary_content_type(request_content_type)
        request_body_chunks = []

        async def receive_wrapper():
            message = await receive()
            if message.get("type") == "http.request":
                body = message.get("body", b"")
                if body and not request_is_binary:
                    request_body_chunks.append(body)
            return message

        response_status = None
        response_headers = {}
        response_content_type = ""
        response_is_binary = False
        response_body_chunks = []

        async def send_wrapper(message):
            nonlocal response_status, response_headers, response_content_type, response_is_binary
            message_type = message.get("type")
            if message_type == "http.response.start":
                response_status = message.get("status")
                response_headers = _headers_to_dict(message.get("headers", []))
                response_content_type = response_headers.get("content-type", "")
                response_is_binary = _is_binary_content_type(response_content_type)
            elif message_type == "http.response.body":
                if not response_is_binary:
                    body = message.get("body", b"")
                    if body:
                        response_body_chunks.append(body)
            await send(message)

        await self.app(scope, receive_wrapper, send_wrapper)

        duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
        request_body_bytes = b"".join(request_body_chunks) if not request_is_binary else b""
        response_body_bytes = b"".join(response_body_chunks) if not response_is_binary else b""

        request_body = _decode_body(request_body_bytes, request_content_type)
        response_body = _decode_body(response_body_bytes, response_content_type)

        if isinstance(request_body, (dict, list)):
            request_body = _redact_tokens(request_body)
        if isinstance(response_body, (dict, list)):
            response_body = _redact_tokens(response_body)

        query_string = scope.get("query_string", b"").decode("latin1")
        query = parse_qs(query_string, keep_blank_values=True)
        query = {key: values[0] if len(values) == 1 else values for key, values in query.items()}
        query = _redact_tokens(query)

        request_headers = _redact_headers(request_headers)
        response_headers = _redact_headers(response_headers)
        if request_is_binary:
            request_body = BINARY_OMITTED
        if response_is_binary:
            response_body = BINARY_OMITTED

        lines = [
            f"HTTP {scope.get('method')} {scope.get('path')}",
            f"client_ip={_get_client_ip(scope)} status={response_status} duration_ms={duration_ms}",
            "query:",
            _indent(_pretty(query)),
            "request_headers:",
            _indent(_pretty(request_headers)),
            "request_body:",
            _indent(_pretty(request_body)),
            "response_headers:",
            _indent(_pretty(response_headers)),
            "response_body:",
            _indent(_pretty(response_body)),
        ]
        logger.info("\n".join(lines))
