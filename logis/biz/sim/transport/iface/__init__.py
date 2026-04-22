from abc import abstractmethod
from typing import TYPE_CHECKING, Any, Generator, List, Optional, Tuple, Union

import simpy
from ipa.decorator import deprecated

from logis.biz.sim.component import ComponentForm as Entity
from logis.biz.sim.const import (
    AgentIdleStrategyOption,
    AgentSelectionStrategyName,
    GoHomeStrategyFrequency,
)
from logis.biz.sim.iface.blueprint import IBlueprint
from logis.data_type import Speed, Time
from logis.iface import Shape
from logis.util import none_if_in
from logis.util.dict_util import get_the_first_existent_key

if TYPE_CHECKING:
    from logis.biz.sim.agent import (
        AgentIdleStrategy,
        IAgentPool,
        IAgentSelectionStrategy,
    )
    from logis.biz.sim.stock import IStock
    from logis.biz.sim.storage import ICell, IRackGroup, IRackSelectionStrategy


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
            entity.properties.get("选择目的地") or entity.properties.get("目的地"),
            "-1",
            "null",
        )
        assert self.destination_id, f"{self.name}未设置目的地"

        self.destination_selection_strategy: Optional[str] = entity.properties.get(
            "目的地选择策略"
        )
        """目的地选择策略"""
        self.retrieval_location_selection_strategy: Optional[str] = (
            entity.properties.get("取料位置选择策略")
        )
        """取料位置选择策略"""

        self.transport_resource_id: str = none_if_in(
            entity.properties.get("选择搬运资源"), "-1", "null"
        )
        assert self.transport_resource_id, f"{self.name}未设置搬运资源"

        _, v = get_the_first_existent_key(
            entity.properties, "搬运资源选择策略", "选择搬运资源策略"
        )
        self.agent_selection_strategy_name: Optional[AgentSelectionStrategyName] = v
        """搬运资源选择策略"""

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

    def get_pickup_strategy(self, **kwargs) -> Optional["IRackSelectionStrategy"]:
        """
        取料位置选择策略
        """
        raise NotImplementedError("get_pickup_strategy not implemented")

    def get_destination_strategy(self, **kwargs) -> Optional["IRackSelectionStrategy"]:
        """
        目的地选择策略
        """
        raise NotImplementedError("get_destination_strategy not implemented")

    @deprecated("use get_destination_strategy or get_pickup_strategy instead")
    def get_rack_selection_strategy(
        self, **kwargs
    ) -> Optional["IRackSelectionStrategy"]:
        """
        货架选择策略

        TODO: 与取料位置选择策略、目的地选择策略合并
        """
        raise NotImplementedError("get_rack_selection_strategy not implemented")

    def get_path_finding_strategy(self, **kwargs):
        """
        路径规划策略
        """
        raise NotImplementedError("get_path_finding_strategy not implemented")

    def get_agent_selection_strategy(
        self, **kwargs
    ) -> Optional["IAgentSelectionStrategy"]:
        """
        智能体选择策略
        """
        raise NotImplementedError("get_agent_selection_strategy not implemented")

    def get_agent_idle_strategy(self, **kwargs) -> Optional["AgentIdleStrategy"]:
        """
        智能体空闲策略
        """
        raise NotImplementedError("get_agent_idle_strategy not implemented")

    @property
    @abstractmethod
    def transport_resource(self) -> Optional["IAgentPool"]:
        """
        所使用的搬运资源
        """
        pass

    @property
    @abstractmethod
    def moving_speed(self) -> Optional[Speed]:
        """
        移动速度
        """
        pass

    def assign_target_location(
        self, *stocks: "IStock", **kwargs
    ) -> Generator[simpy.Event, Any, Tuple[List["IStock"], Optional["IStock"]]]:
        """
        为货物分配目标位置

        Args:
            stocks: 货物列表

        Returns:
            Tuple[List["Stock"], Optional["Stock"]]: 成功的货物列表、未分配的货物
        """
        raise NotImplementedError("assign_target_location not implemented")
