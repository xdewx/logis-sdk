from abc import ABC
from typing import Iterable, Protocol, Self, Type, runtime_checkable

from ..data_type import ComponentConfigItem


class IComponent(ABC):
    """
    类型标识
    历史逻辑区分蓝图和空间标记两种概念，为了统一衍生出此接口
    但后续在改造的过程中，逐步把空间标记也视为蓝图，因此此接口似乎就没太多必要，不过作为更抽象的接口，还是保留着
    """

    def __init__(self, *args, **kwargs):
        pass

    def is_valid(self):
        """
        判断组件是否有效
        """
        return True

    def previous_nodes(self, direct: bool = True, **kwargs) -> Iterable[Self]:
        """
        获取上游节点
        Args:
            direct (bool, optional): 是否只获取直接上游节点。默认值为True。
        """
        raise NotImplementedError("previous_nodes method not implemented")

    def next_nodes(self, direct: bool = True, **kwargs) -> Iterable[Self]:
        """
        获取下游节点
        Args:
            direct (bool, optional): 是否只获取直接下游节点。默认值为True。
        """
        raise NotImplementedError("next_nodes method not implemented")


@runtime_checkable
class ComponentLoader(Protocol):
    """
    组件加载器、解析器
    """

    def load(self, item: ComponentConfigItem) -> Type[IComponent]:
        """
        加载组件
        Args:
            item (ComponentConfigItem): 组件配置项
        Returns:
            Type[IComponent]: 组件类
        """
        raise NotImplementedError("load method not implemented")
