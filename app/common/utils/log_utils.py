from loguru import logger
import os
import sys
import threading

from app.core.config import settings

REQUEST_RESPONSE_LOGGER_NAME = "request_response"
DEBUG_LEVELS = {"TRACE", "DEBUG"}
INFO_LEVELS = {"INFO", "SUCCESS"}
WARNING_LEVELS = {"WARNING"}
ERROR_LEVELS = {"ERROR", "CRITICAL"}


def _format_record(record):
    extra_name = record["extra"].get("name")
    name = extra_name if extra_name else record["name"]
    message = record["message"]
    if "{" in message or "}" in message:
        message = message.replace("{", "{{").replace("}", "}}")
    return f"{record['time']:YYYY-MM-DD HH:mm:ss} | {record['level']} | {name}:{record['line']} - {message}\n"


class LoguruLogger:
    _instance = None
    _initialized = False
    _handlers = {}  # 类级别的处理器字典
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, log_dir=settings.log_dir, level="INFO", rotation="10 MB", retention="7 days", enqueue=True):
        if self._initialized:
            return
        with self._lock:
            if self._initialized:
                return

            self.log_dir = log_dir
            self.level = level
            self.rotation = rotation
            self.retention = retention
            self.enqueue = enqueue

            # 确保日志目录存在
            os.makedirs(self.log_dir, exist_ok=True)

            # 清除默认的logger配置
            logger.remove()

            # 控制台输出（只添加一次）
            self._handlers['console'] = logger.add(
                sys.stderr,
                level=level,
                format=_format_record
            )

            def build_level_filter(level_names):
                def level_filter(record):
                    if record["extra"].get("name") == REQUEST_RESPONSE_LOGGER_NAME:
                        return False
                    return record["level"].name in level_names

                return level_filter

            def request_response_filter(record):
                return record["extra"].get("name") == REQUEST_RESPONSE_LOGGER_NAME

            self._handlers['debug'] = logger.add(
                os.path.join(self.log_dir, "debug.log"),
                level="TRACE",
                rotation=self.rotation,
                retention=self.retention,
                encoding="utf-8",
                enqueue=self.enqueue,
                format=_format_record,
                filter=build_level_filter(DEBUG_LEVELS),
            )

            self._handlers['info'] = logger.add(
                os.path.join(self.log_dir, "info.log"),
                level="TRACE",
                rotation=self.rotation,
                retention=self.retention,
                encoding="utf-8",
                enqueue=self.enqueue,
                format=_format_record,
                filter=build_level_filter(INFO_LEVELS),
            )

            self._handlers['warning'] = logger.add(
                os.path.join(self.log_dir, "warning.log"),
                level="TRACE",
                rotation=self.rotation,
                retention=self.retention,
                encoding="utf-8",
                enqueue=self.enqueue,
                format=_format_record,
                filter=build_level_filter(WARNING_LEVELS),
            )

            self._handlers['error'] = logger.add(
                os.path.join(self.log_dir, "error.log"),
                level="TRACE",
                rotation=self.rotation,
                retention=self.retention,
                encoding="utf-8",
                enqueue=self.enqueue,
                format=_format_record,
                filter=build_level_filter(ERROR_LEVELS),
            )

            self._handlers['request_response'] = logger.add(
                os.path.join(self.log_dir, "request_response.log"),
                level="TRACE",
                rotation=self.rotation,
                retention=self.retention,
                encoding="utf-8",
                enqueue=self.enqueue,
                format=_format_record,
                filter=request_response_filter,
            )

            self._initialized = True

    def get_logger(self, module_name="default"):
        return logger.bind(name=module_name)


log_util = LoguruLogger()
