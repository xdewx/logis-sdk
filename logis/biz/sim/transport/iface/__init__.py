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

    def get_pickup_strategy(self, **kwargs):
        """
        取料位置选择策略
        """
        raise NotImplementedError("get_pickup_strategy not implemented")

    def get_destination_strategy(self, **kwargs):
        """
        目的地选择策略
        """
        raise NotImplementedError("get_destination_strategy not implemented")

    def get_path_finding_strategy(self, **kwargs):
        """
        路径规划策略
        """
        raise NotImplementedError("get_path_finding_strategy not implemented")

    def get_agent_selection_strategy(self, **kwargs):
        """
        智能体选择策略
        """
        raise NotImplementedError("get_agent_selection_strategy not implemented")

    def get_agent_idle_strategy(self, **kwargs):
        """
        智能体空闲策略
        """
        raise NotImplementedError("get_agent_idle_strategy not implemented")
