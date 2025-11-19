import logging
import logging.handlers
from collections import defaultdict
from typing import Any, Dict, List, Optional
from uuid import uuid4

from colorlog import ColoredFormatter

from logis.util.pkg_util import get_class_full_path

from .fmt import LoggerFormat


def add_formatter_if_not(handler: logging.Handler) -> None:
    """
    如果给定的handler上尚未配置formatter， 则为其设置默认的formatter。
    """
    if not handler:
        return
    if handler.formatter is not None:
        return
    if isinstance(handler, logging.FileHandler):
        handler.setFormatter(logging.Formatter(LoggerFormat.DEFAULT.value))
    else:
        handler.setFormatter(ColoredFormatter(LoggerFormat.COLORED_DEFAULT.value))


def get_dict_config_tmpl():
    """
    获取默认的 logging.config.dictConfig 字典配置模板
    """
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": defaultdict(dict),
        "filters": defaultdict(dict),
        "handlers": defaultdict(dict),
        "loggers": defaultdict(dict),
    }


def formatter_to_dict(formatter: logging.Formatter) -> Dict[str, Any]:
    """
    将 logging.Formatter 实例转换为 logging.config.dictConfig 兼容的字典配置
    """
    return {
        "class": get_class_full_path(formatter.__class__),
        "format": formatter._fmt,
        "datefmt": formatter.datefmt,
    }


def get_name_attr(obj: Any) -> str:
    """
    获取对象的名称， 如果对象没有名称，则返回其类型名。
    """
    return getattr(obj, "name", None)


def handler_to_dict(handler: logging.Handler) -> Dict[str, Any]:
    """
    将 logging.Handler 实例转换为 logging.config.dictConfig 兼容的字典配置
    """
    formatter = getattr(handler, "formatter", None)
    formatter_name = getattr(formatter, "name", None)
    handler_args: Dict[str, Any] = {
        "class": get_class_full_path(handler.__class__),
        "level": handler.level,
        "formatter": formatter_name,
        "filters": [
            get_name_attr(f)
            for f in handler.filters
            if isinstance(f, logging.Filter) and get_name_attr(f) is not None
        ],
    }
    if isinstance(handler, logging.FileHandler):
        handler_args["filename"] = handler.baseFilename
        handler_args["mode"] = handler.mode
        handler_args["encoding"] = handler.encoding
    elif isinstance(handler, logging.StreamHandler):
        try:
            fileno = handler.stream.fileno()
            handler_args["stream"] = (
                "ext://sys.stdout" if fileno == 1 else "ext://sys.stderr"
            )
        except (AttributeError, OSError):
            handler_args["stream"] = "ext://sys.stdout"
    else:
        raise ValueError(f"Unsupported handler type: {handler}")

    if isinstance(handler, logging.handlers.RotatingFileHandler):
        handler_args["maxBytes"] = handler.maxBytes
        handler_args["backupCount"] = handler.backupCount
    elif isinstance(handler, logging.handlers.TimedRotatingFileHandler):
        handler_args["when"] = handler.when
        handler_args["interval"] = handler.interval
        handler_args["backupCount"] = handler.backupCount

    return handler_args


class DictConfigBuilder:
    """
    支持从对象实例中提取配置，
    并将其转换为 logging.config.dictConfig 兼容的字典配置
    """

    def __init__(self):
        self.__dict_config__ = get_dict_config_tmpl()
        self.__loggers__: Dict[str, Dict[str, Any]] = self.__dict_config__["loggers"]
        self.__handlers__: Dict[str, Dict[str, Any]] = self.__dict_config__["handlers"]
        self.__filters__: Dict[str, Dict[str, Any]] = self.__dict_config__["filters"]
        self.__formatters__: Dict[str, Dict[str, Any]] = self.__dict_config__[
            "formatters"
        ]

    def build(self):
        return self.__dict_config__

    def filter(self, f: logging.Filter, name: str | None = None) -> Dict[str, Any]:
        """
        将 logging.Filter 实例转换为 logging.config.dictConfig 兼容的字典配置

        返回格式符合 Python logging 官方 dict 配置规范，支持直接用于 dictConfig()
        """
        if not isinstance(f, logging.Filter):
            logging.warning("only logging.Filter instance supported now: %s", f)
            return self
        name = name if name is not None else get_name_attr(f)
        setattr(f, "name", name)
        filter_dict: dict = self.__filters__[name]
        filter_dict.update({"()": get_class_full_path(f.__class__)})
        return self

    def handler(
        self, handler: logging.Handler, name: str | None = None
    ) -> Dict[str, Any]:
        """
        将 logging.Handler 实例转换为 logging.config.dictConfig 兼容的字典配置

        返回格式符合 Python logging 官方 dict 配置规范，支持直接用于 dictConfig()
        """
        name = name if name is not None else handler.name
        if name is None:
            name = str(uuid4())
        handler.name = name

        for f in handler.filters:
            if get_name_attr(f) is None:
                setattr(f, "name", str(uuid4()))

        if formatter := getattr(handler, "formatter", None):
            formatter_name = getattr(formatter, "name", None)
            if formatter_name is None:
                formatter_name = str(uuid4())
            setattr(formatter, "name", formatter_name)

        handler_dict = handler_to_dict(handler)
        formatter = getattr(handler, "formatter", None)
        if formatter is not None:
            self.formatter(formatter)
        for f in handler.filters:
            self.filter(f)
        self.__handlers__[name].update(handler_dict)
        return self

    def formatter(
        self, formatter: logging.Formatter, name: str | None = None
    ) -> Dict[str, Any]:
        """
        将 logging.Formatter 实例转换为 logging.config.dictConfig 兼容的字典配置

        返回格式符合 Python logging 官方 dict 配置规范，支持直接用于 dictConfig()
        """
        if formatter is None:
            return self
        name = name or getattr(formatter, "name", None)
        setattr(formatter, "name", name)
        formatter_dict = formatter_to_dict(formatter)
        self.__formatters__[name].update(formatter_dict)
        return self

    def logger(self, logger: logging.Logger) -> Dict[str, Any]:
        """
        将 logging.Logger 实例转换为 logging.config.dictConfig 兼容的字典配置

        返回格式符合 Python logging 官方 dict 配置规范，支持直接用于 dictConfig()
        """
        if logger is None:
            return self
        logger_dict: dict = self.__loggers__[logger.name]
        handler_ids = []
        for handler in logger.handlers:
            self.handler(handler)
            handler_ids.append(handler.name)

        logger_dict.update(
            {
                "level": logger.getEffectiveLevel(),
                "propagate": "yes" if logger.propagate else "no",
                "handlers": handler_ids,
            }
        )

        return self
