from abc import abstractmethod
from typing import TYPE_CHECKING, Optional, Union

from logis.biz.sim.component import ComponentForm as Entity
from logis.biz.sim.const import (
    AgentIdleStrategyOption,
    AgentSelectionStrategyName,
    GoHomeStrategyFrequency,
    OperationType,
)
from logis.biz.sim.iface.blueprint import IBlueprint
from logis.data_type import Time
from logis.iface import Shape
from logis.util import none_if_in
from logis.util.dict_util import get_the_first_existent_key

if TYPE_CHECKING:
    from logis.biz.sim.agent import IAgentPool
    from logis.biz.sim.storage import ICell, IRackGroup


class ITransportBlueprint(IBlueprint):
    """
    搬运蓝图基类
    """

    def __init__(self, entity: Entity, *args, **kwargs):
        super().__init__(entity, *args, **kwargs)

        # 位置相关
        self.pickup_location_id: Optional[str] = none_if_in(
            entity.properties.get("取料位置", entity.properties.get("取货位置")),
            "-1",
            "null",
        )
        self.destination_id: str = none_if_in(
            entity.properties.get("目的地"), "-1", "null"
        )
        self.destination_selection_strategy = entity.properties.get("目的地选择策略")

        # 资源相关
        self.retrieval_location_selection_strategy = entity.properties.get(
            "取料位置选择策略"
        )
        """取料位置选择策略"""

        _, v = get_the_first_existent_key(
            entity.properties, "搬运资源选择策略", "选择搬运资源策略"
        )
        self.agent_selection_strategy_name: Optional[AgentSelectionStrategyName] = v
        """搬运资源选择策略"""

        # 时间相关
        self.loading_time = Time.parse_str(entity.properties.get("装载时间", "0|秒"))
        """装载时间"""
        self.unloading_time = Time.parse_str(entity.properties.get("卸载时间", "0|秒"))
        """卸载时间"""
        self._moving_speed = none_if_in(
            entity.properties.get("移动速度"), "DefaultValue"
        )

        # 资源释放策略
        release_str: str = entity.properties.get("释放资源后", "")
        release_config = release_str.split("|")
        self.after_release_resource: AgentIdleStrategyOption = (
            release_config[0] if len(release_config) > 0 else ""
        )
        self.go_home_frequency: GoHomeStrategyFrequency = (
            release_config[1].split(":")[1] if len(release_config) > 1 else ""
        )

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

    @property
    def transport_resource(self) -> Optional["IAgentPool"]:
        pass
