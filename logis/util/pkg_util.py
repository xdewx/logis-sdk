import inspect
import logging
from importlib import import_module
from types import ModuleType
from typing import Callable, List, Set, Tuple, Type

import hmr
from watchfiles import Change, PythonFilter, awatch


def try_hot_reload(name, package: str | None = None):
    """
    热加载指定模块
    Args:
        name: 模块名
        package: 包名
    """
    try:
        hmlib = import_module(name=name, package=package)
        logging.info("shall reload: %s", hmlib)
        hmr.reload(hmlib)
    except Exception as e:
        logging.warning("failed to reload: %s", e)


async def watch_python_dir(
    dir: str, on_change: Callable[[Set[Tuple[Change, str]]], None]
):
    """
    这是一个使用样例，功能并不通用
    """
    logging.info("watch files in %s", dir)
    async for change in awatch(str(dir), watch_filter=PythonFilter()):
        logging.info("change detected:%s", change)
        on_change(change)


def collect_subclass_of[T](
    base_class: Type[T], _from: ModuleType, include_base_class: bool = False
):
    def predicate(m):
        if not include_base_class and m is base_class:
            return False
        return inspect.isclass(m) and issubclass(m, base_class)

    name_class_map: List[Tuple[str, T]] = inspect.getmembers(_from, predicate=predicate)
    return name_class_map
