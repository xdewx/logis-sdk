from abc import abstractmethod
from typing import List, Optional, TypeVar

from logis.iface import IControl
from logis.task import ITaskHandler

from ..data_type.component import BlueprintKind
from .component import IComponent
from .proxy import ISimProxy


class IBlueprint(ISimProxy, ITaskHandler, IComponent, IControl):
    """
    所有蓝图组件的抽象基类
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name: Optional[str] = None
        self.create_edit_id: Optional[str] = None
        self.type_id: Optional[str] = None
        self.type_name: Optional[str] = None

    @classmethod
    def verbose_name(cls, *args, **kwargs):
        return cls.__name__

    @staticmethod
    @abstractmethod
    def kinds(*args, **kwargs) -> List[BlueprintKind]:
        """
        之所以有这个，是因为历史逻辑依靠此标志来分组
        """
        pass


BlueprintClass = TypeVar("BlueprintClass", bound=IBlueprint)
