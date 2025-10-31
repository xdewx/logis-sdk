import logging
import sys
from logging import StreamHandler
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from pathlib import Path
from typing import Type

from platformdirs import user_data_dir

from logis._log.fmt import LoggerFormat
from logis._log.handler import set_default_formatter


class LoggerBuilder:
    """
    日志构建器接口
    """

    def __init__(self, **kwargs) -> None:
        self.dir(Path(user_data_dir()) / "logs").name("root").level(
            logging.WARNING
        ).encoding("utf-8").backup_count(5).rotation_when("h").max_bytes(
            200 * 1024 * 1024
        )

        self._handlers = []

    def _resolve_file_path(self, file_name: str) -> Path:
        assert file_name is not None, "File name must be provided for file handlers."
        if not file_name.endswith(".log"):
            file_name += ".log"

        if self._log_dir:
            return self._log_dir.joinpath(file_name)
        return Path(file_name)

    def name(self, name: str) -> "LoggerBuilder":
        """
        设置日志名称
        """
        self._name = name
        return self

    def dir(self, path: str | Path) -> "LoggerBuilder":
        """
        设置日志目录
        """
        self._log_dir = path if isinstance(path, Path) else Path(path)
        self._log_dir.mkdir(parents=True, exist_ok=True)
        logging.debug("Log directory set to: %s", str(self._log_dir))
        return self

    def level(self, level: int = logging.WARNING) -> "LoggerBuilder":
        """
        设置root日志级别
        """
        self._level = level
        return self

    def max_bytes(self, max_bytes: int) -> "LoggerBuilder":
        """
        设置日志文件最大字节数
        """
        self._max_bytes = max_bytes
        return self

    def encoding(self, encoding: str) -> "LoggerBuilder":
        """
        设置日志文件编码
        """
        self._encoding = encoding
        return self

    def backup_count(self, count: int) -> "LoggerBuilder":
        """
        设置日志文件最大备份数量
        """
        self._backup_count = count
        return self

    def rotation_when(self, when: str) -> "LoggerBuilder":
        """
        设置日志文件轮转时间间隔单位
        """
        self._rotation_when = when
        return self

    def add_handler(
        self,
        handler_type: Type[logging.Handler],
        level: int | None = None,
        fmt: LoggerFormat | None = LoggerFormat.DEFAULT,
        file_name: str | None = None,
        **kwargs
    ) -> "LoggerBuilder":
        """
        添加日志处理器
        """
        if handler_type is TimedRotatingFileHandler:
            handler = TimedRotatingFileHandler(
                filename=self._resolve_file_path(file_name),
                when=self._rotation_when,
                backupCount=self._backup_count,
                encoding=self._encoding,
                **kwargs
            )
        elif handler_type is RotatingFileHandler:
            handler = RotatingFileHandler(
                filename=self._resolve_file_path(file_name),
                maxBytes=self._max_bytes,
                backupCount=self._backup_count,
                encoding=self._encoding,
                **kwargs
            )
        elif handler_type is StreamHandler:
            handler = StreamHandler(stream=kwargs.get("stream", sys.stdout))
        else:
            handler = handler_type(**kwargs)

        set_default_formatter(handler)

        if level is not None:
            handler.setLevel(level)
        else:
            handler.setLevel(self._level)

        self._handlers.append(handler)
        return self

    def build(self) -> logging.Logger:
        logger = logging.getLogger(self._name)
        logger.setLevel(self._level)
        logger.propagate = False
        for handler in self._handlers:
            logger.addHandler(handler)
        return logger


def get_logger(name: str) -> logging.Logger:
    return LoggerBuilder().name(name).add_handler(StreamHandler).build()
