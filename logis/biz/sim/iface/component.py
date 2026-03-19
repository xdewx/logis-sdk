from abc import ABCMeta
from typing import Protocol, Type, runtime_checkable

from ..data_type import ComponentConfigItem


class IComponent(metaclass=ABCMeta):
    """
    类型标识
    """

    def __init__(self, *args, **kwargs):
        self.create_edit_id: str = None

    def is_valid(self):
        return True


@runtime_checkable
class ComponentLoader(Protocol):
    """
    组件加载器、解析器
    """

    def load(self, item: ComponentConfigItem) -> Type[IComponent]:
        pass
