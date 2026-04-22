from abc import abstractmethod
from typing import TYPE_CHECKING, Any, Generator, List, Optional, Tuple, Union

import simpy
from ipa.decorator import deprecated

from logis.biz.sim.agent import (
    AgentIdleStrategy,
    IAgentPool,
    IAgentSelectionStrategy,
)
from logis.biz.sim.component import ComponentForm as Entity
from logis.biz.sim.const import (
    AgentIdleStrategyOption,
    AgentSelectionStrategyName,
    GoHomeStrategyFrequency,
)
from logis.biz.sim.iface.blueprint import IBlueprint
from logis.biz.sim.storage import IRackSelectionStrategy
from logis.data_type import Speed, Time
from logis.util import none_if_in
from logis.util.dict_util import get_the_first_existent_key

if TYPE_CHECKING:
    from logis.biz.sim import Location
    from logis.biz.sim.stock import IStock


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
        self.__destination_strategy__: Optional[IRackSelectionStrategy] = None
        self.retrieval_location_selection_strategy: Optional[str] = (
            entity.properties.get("取料位置选择策略")
        )
        """取料位置选择策略"""
        self.__pickup_strategy__: Optional[IRackSelectionStrategy] = None

        self.transport_resource_id: str = none_if_in(
            entity.properties.get("选择搬运资源"), "-1", "null"
        )
        assert self.transport_resource_id, f"{self.name}未设置搬运资源"

        _, v = get_the_first_existent_key(
            entity.properties, "搬运资源选择策略", "选择搬运资源策略"
        )
        self.agent_selection_strategy_name: Optional[AgentSelectionStrategyName] = v
        """搬运资源选择策略"""
        self.__agent_selection_strategy__: Optional[IAgentSelectionStrategy] = None

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
        self.__agent_idle_strategy__: Optional[AgentIdleStrategy] = None

    @property
    @abstractmethod
    def pickup_location(self) -> Optional["Location"]:
        """
        取料位置
        """
        from logis.biz.sim import ILocationGetter

        inst = self.context.resolve_code_strategy(
            self.pickup_location_id, ILocationGetter, ctx=self.context
        )
        return inst.get() if inst else None

    @property
    @abstractmethod
    def destination(self) -> Optional["Location"]:
        """
        目的地
        """
        from logis.biz.sim import ILocationGetter

        inst = self.context.resolve_code_strategy(
            self.destination_id, ILocationGetter, ctx=self.context
        )
        return inst.get() if inst else None

    def get_pickup_strategy(self, **kwargs) -> Optional["IRackSelectionStrategy"]:
        """
        取料位置选择策略
        """
        if not self.__pickup_strategy__:
            self.__pickup_strategy__ = self.context.resolve_code_strategy(
                self.retrieval_location_selection_strategy,
                IRackSelectionStrategy,
                ctx=self.context,
            )
        return self.__pickup_strategy__

    def get_destination_strategy(self, **kwargs) -> Optional["IRackSelectionStrategy"]:
        """
        目的地选择策略
        """
        if not self.__destination_strategy__:
            self.__destination_strategy__ = self.context.resolve_code_strategy(
                self.destination_selection_strategy,
                IRackSelectionStrategy,
                ctx=self.context,
            )
        return self.__destination_strategy__

    @deprecated("use get_destination_strategy instead")
    def get_rack_selection_strategy(
        self, **kwargs
    ) -> Optional["IRackSelectionStrategy"]:
        """
        货架选择策略（原目的地选择策略）
        """
        return self.get_destination_strategy(**kwargs)

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
        if not self.__agent_selection_strategy__:
            self.__agent_selection_strategy__ = self.context.resolve_code_strategy(
                self.agent_selection_strategy_name,
                IAgentSelectionStrategy,
                ctx=self.context,
                agent_pool=self.transport_resource,
            )

        if self.__agent_selection_strategy__ is None:
            from logis.biz.sim.agent import DefaultAgentSelectionStrategy

            self.__agent_selection_strategy__ = DefaultAgentSelectionStrategy(
                ctx=self.context, agent_pool=self.transport_resource
            )
        return self.__agent_selection_strategy__

    def get_agent_idle_strategy(self, **kwargs) -> Optional["AgentIdleStrategy"]:
        """
        智能体空闲策略
        """
        if self.__agent_idle_strategy__ is not None:
            return self.__agent_idle_strategy__
        if self.after_release_resource == "返回到归属地位置":
            from logis.biz.sim.agent import GoHomeStrategy

            self.__agent_idle_strategy__ = GoHomeStrategy(
                frequency=self.go_home_frequency, env=self.env, ctx=self.context
            )
        elif self.after_release_resource == "停留在原地":
            self.__agent_idle_strategy__ = None
        else:
            self.__agent_idle_strategy__ = self.context.resolve_code_strategy(
                self.after_release_resource,
                AgentIdleStrategy,
                ctx=self.context,
            )
        return self.__agent_idle_strategy__

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
