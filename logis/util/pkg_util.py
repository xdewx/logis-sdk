import inspect
import logging
from importlib import import_module
from types import ModuleType
from typing import Callable, List, Optional, Set, Tuple, Type, TypeVar

import hmr
from watchfiles import Change, PythonFilter, awatch


def try_import(path: str):
    """
    支持以x.y.z的方式导入模块或模块内的属性
    Args:
        path: 模块路径或属性路径
    Returns:
        导入的模块或属性, 如果导入失败则返回None
    """
    try:
        return import_module(path)
    except ModuleNotFoundError:
        tmps = path.split(".")
        assert len(tmps) > 1, f"unexpected path: {path}"
        module = try_import(".".join(tmps[0:-1]))
        return getattr(module, tmps[-1], None)
    except Exception as e:
        logging.warning("failed to import %s: %s", path, e)
        return None


def try_hot_reload(name, package: Optional[str] = None):
    """
    热加载指定模块
    Args:
        name: 模块名
        package: 包名
    """
    try:
        hmlib = import_module(name=name, package=package)
        assert hmlib, f"failed to import module: {package}.{name}"
        logging.info("shall reload: %s", hmlib)
        # TODO: exclude怎么用
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


T = TypeVar("T")


def is_subclass_of(
    child: Type[T], parent: Type[T], include_parent: bool = True
) -> bool:
    """
    判断child是否是parent的子类
    Args:
        child: 子类
        parent: 父类
        include_parent: 父类本身是否视为子类
    Returns:
        是否是子类
    """
    if (not include_parent) and (child is parent):
        return False
    return inspect.isclass(child) and issubclass(child, parent)

def collect_subclass_of(
    parent: Type[T], _from: ModuleType, include_parent: bool = False
):
    """
    收集所有子类
    Args:
        parent: 父类
        _from: 模块
        include_parent: 父类本身是否视为子类
    Returns:
        所有子类的(名称,类,全路径)元组
    """

    def predicate(child):
        return is_subclass_of(child=child, parent=parent, include_parent=include_parent)

    name_class_map: List[Tuple[str, T]] = inspect.getmembers(_from, predicate=predicate)
    return name_class_map


def get_class_full_path(cls) -> str:
    """
    获取类的全路径表示（模块路径.类名）

    参数:
        cls: 目标类（需传入类本身，而非实例）

    返回:
        str: 类的全路径，格式为 "模块路径.类名"
    """
    # __qualname__ 获取类的限定名（含嵌套关系，如 "OuterClass.InnerClass"）
    return f"{cls.__module__}.{cls.__qualname__}"
