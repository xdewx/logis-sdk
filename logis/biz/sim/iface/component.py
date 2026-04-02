from abc import ABC
from typing import Protocol, Type, runtime_checkable

from ..data_type import ComponentConfigItem


class IComponent(ABC):
    """
    类型标识
    """

    def __init__(self, *args, **kwargs):
        pass

    def is_valid(self):
        return True


@runtime_checkable
class ComponentLoader(Protocol):
    """
    组件加载器、解析器
    """

    def load(self, item: ComponentConfigItem) -> Type[IComponent]:
        raise NotImplementedError("load method not implemented")
