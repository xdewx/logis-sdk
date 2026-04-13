from abc import abstractmethod
from typing import TYPE_CHECKING, Union

from logis.biz.sim.iface.blueprint import IBlueprint
from logis.iface import Shape

if TYPE_CHECKING:
    from logis.biz.sim.storage import ICell, IRackGroup


class ITransportBlueprint(IBlueprint):
    """
    搬运蓝图
    """

    @property
    @abstractmethod
    def pickup_location(self) -> Union["IRackGroup", "ICell", Shape, None]:
        """
        取料位置
        """
        pass

    @property
    @abstractmethod
    def destination(self) -> Union["IRackGroup", "ICell", Shape, None]:
        """
        目的地
        """
        pass
