from abc import abstractmethod
from typing import TYPE_CHECKING, Any, Generator, List, Literal, Optional, Tuple, Union

import simpy
from ipa.decorator import deprecated
from more_itertools import first

from logis.alg.path_finding import (
    PathFindingAlgorithm,
    default_algorithm_matcher,
    find_algorithm,
)
from logis.biz.sim.agent import (
    AgentIdleStrategy,
    IAgent,
    IAgentPool,
    IAgentSelectionStrategy,
)
from logis.biz.sim.component import ComponentForm as Entity
from logis.biz.sim.const import (
    AgentIdleStrategyOption,
    AgentSelectionStrategyName,
    GoHomeStrategyFrequency,
)
from logis.biz.sim.iface.blueprint import IBlueprint, TaskManifest
from logis.biz.sim.storage import IRackSelectionStrategy
from logis.data_type import Speed, Time
from logis.task import ITask
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

        self.pathfinding_alg_name: str = entity.properties.get("寻路算法", "A*")
        """寻路算法名，默认A*算法"""
        self.__path_finding_strategy__: Optional[PathFindingAlgorithm] = None

        self._pickup_task_manifest = TaskManifest(component_id=self.create_edit_id)
        """取料任务清单"""
        self._delivery_task_manifest = TaskManifest(component_id=self.create_edit_id)
        """交付任务清单"""

        self._pickup_lock = simpy.Resource(self.env, capacity=1)
        """取料任务锁"""
        self._delivery_lock = simpy.Resource(self.env, capacity=1)
        """交付任务锁"""

    def infer_working_stage(self, stocks: List["IStock"]):
        """
        获取当前工作阶段
        """
        demo_stock = first(stocks, None)

        if not demo_stock:
            return None
        return demo_stock.__stage__

    def get_task_manifest(self, stage: Literal["pickup", "delivery"]) -> TaskManifest:
        """
        由于搬运具有取料和交付两种任务，
        因此需要分别设置取料任务清单和交付任务清单。

        Args:
            stage (Literal["pickup", "delivery"]): 任务阶段

        Returns:
            TaskManifest: 任务清单
        """
        if stage == "pickup":
            return self._pickup_task_manifest
        elif stage == "delivery":
            return self._delivery_task_manifest
        else:
            raise ValueError(f"{self.name}未知任务阶段: {stage}")

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

    def get_pickup_strategy(self, **kwargs):
        """
        取料位置选择策略
        如果没有设置取料位置选择策略，尝试从前一个蓝图块获取
        """
        if self.__pickup_strategy__:
            return self.__pickup_strategy__

        from logis.biz.sim import BlueprintKind

        strategy = self.retrieval_location_selection_strategy

        # 兼容历史逻辑：如果没有取料位置选择策略，尝试从前一个蓝图块获取
        if not strategy:
            for node in self.previous_nodes(direct=True):
                if node.is_kind_of(BlueprintKind.ENTER):
                    # Enter节点可能有相关的策略
                    strategy = node.selection_policy
                    if strategy:
                        break
                elif node.is_kind_of(BlueprintKind.SOURCE):
                    # Source节点可能有相关的策略
                    strategy = node.generate_strategy
                    if strategy:
                        break
        self.__pickup_strategy__ = self.context.resolve_code_strategy(
            strategy,
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

    def get_path_finding_strategy(self, **kwargs) -> Union[PathFindingAlgorithm, None]:
        """
        路径规划策略
        """
        if self.__path_finding_strategy__:
            return self.__path_finding_strategy__

        from logis.alg.path_finding import AStarPathFinding

        alg_class = find_algorithm(
            default_algorithm_matcher,
            alg_name=self.pathfinding_alg_name.lower() or "a_star",
            space=dict(a_star=AStarPathFinding) | {"a*": AStarPathFinding},
        )

        if alg_class:
            self.__path_finding_strategy__ = alg_class()
        else:
            self.__path_finding_strategy__ = self.context.resolve_code_strategy(
                self.pathfinding_alg_name, PathFindingAlgorithm, ctx=self.context
            )

        return self.__path_finding_strategy__

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

    def can_return_original_place(self, agent: Union["IAgent"], **kwargs):
        """
        检查指定智能体是否可以返回原始位置

        Args:
            agent: 智能体

        Returns:
            bool: 是否可以返回原始位置
        """
        if not agent.is_task_all_done():
            return False

        if self.go_home_frequency == "如果无其他任务":
            # FIXME: 此处判断逻辑待完善
            return self.get_task_manifest("delivery").no_stock_task_left()

        return True

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

    def transport_item(
        self,
        object: Union[List["IStock"], "IStock"],
        task_type: str,
        order: Optional["ITask"] = None,
        agent: Optional["IAgent"] = None,
        **kwargs,
    ) -> Generator[simpy.Event, Any, Optional["IStock"]]:
        """
        单次运输货物

        Args:
            object: 待运输目标
            task_type: 任务类型
            order: 对应的订单,如果所有货物属于同一个订单，否则应从货物中获取order_id
            agent: 所使用的智能体，如果不传，则应在此方法内部分配、释放智能体

        Returns:
            Optional["IStock"]: 运输成功返回运输的货物，否则返回None

        Yields:
            simpy.Event: 运输事件
        """

        raise NotImplementedError("transport_item not implemented")
