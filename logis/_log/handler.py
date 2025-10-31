import logging
import sys
from logging import StreamHandler

from colorlog import ColoredFormatter

from logis._log.fmt import LoggerFormat


def new_handler(handler: type[logging.Handler], **kwargs) -> logging.Handler:
    """
    创建一个新的日志处理器实例
    """
    raise NotImplementedError(f"new_handler({handler.__name__})")


DEFAULT_CONSOLE_HANDLER = StreamHandler(sys.stdout)


def set_default_formatter(handler: logging.Handler) -> None:
    if not handler:
        return
    if handler.formatter is not None:
        return
    if isinstance(handler, StreamHandler):
        handler.setFormatter(ColoredFormatter(LoggerFormat.COLORED_DEFAULT.value))
    else:
        handler.setFormatter(logging.Formatter(LoggerFormat.DEFAULT.value))
