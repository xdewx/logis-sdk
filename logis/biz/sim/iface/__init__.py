__doc__ = """
仿真模块接口
"""

from typing import Protocol

from logis.task import ITaskHandler

from ..data_type import BlueprintKind
from .component import *
from .order import *
from .picking import *
from .wave import *


class ISim(ABC):
    """
    仿真模块接口
    """


@runtime_checkable
class IControl(Protocol):
    """
    控制器，用于控制仿真的进行
    """

    disabled: bool = False


class IBlueprint(IComponent, ISim, IControl, ITaskHandler):
    """
    所有蓝图组件的抽象基类
    """

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


from logis.iface import IRegistry


class IBlueprintRegistry(IRegistry[IBlueprint]):
    """
    蓝图注册中心
    """
