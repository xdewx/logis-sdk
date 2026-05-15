from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Generator, Optional, TypeVar, Union

import simpy

from logis.biz.sim import AgentId, IBlueprint, LocationType
from logis.biz.sim.component import IGrid
from logis.biz.sim.graph import ISimPathGraph
from logis.data_type import Length, Point, Speed, ThreeDimensionalVelocity, Time

if TYPE_CHECKING:
    from logis.alg.path_finding import PathFindingAlgorithm

class IAgent(IBlueprint):
    """
    智能体抽象基类
    """

    @abstractmethod
    def record_movement(self, start: Point, end: Point, duration: float, **kwargs):
        """
        记录移动

        Args:
            start (Point): 移动起始点
            end (Point): 移动目标点
            duration (float): 移动时间以seconds为单位
        """
        pass

    @abstractmethod
    def resolve_binding_graph(self, *args, **kwargs) -> Union["IGrid", "ISimPathGraph"]:
        """
        获取智能体绑定的地图
        """
        pass

    @abstractmethod
    def resolve_center_point(self) -> Optional[Point]:
        """
        获取智能体的中心点
        """
        pass

    @property
    @abstractmethod
    def id(self) -> AgentId:
        pass

    @property
    @abstractmethod
    def rack_as_obstacle(self) -> bool:
        """
        是否将其余货架视为障碍物
        """
        pass

    @property
    @abstractmethod
    def agent_as_obstacle(self) -> bool:
        """
        是否将其余智能体视为障碍物
        """
        pass

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.origin_location: Optional[Point] = None
        """初始位置"""
        # TODO: 这里主要是因为Stock是个特例，后续考虑分离
        self.current_location: Optional[LocationType] = None
        """当前位置"""
        self.path_finding_strategy: Optional["PathFindingAlgorithm"] = None
        """寻路策略"""

    @property
    @abstractmethod
    def is_free(self, **kwargs) -> bool:
        """
        判断是否空闲
        """
        pass

    @abstractmethod
    def stop_working(self, *args, **kwargs):
        pass

    @abstractmethod
    def start_working(self, *args, **kwargs):
        pass

    @abstractmethod
    def do_move(
        self, next_point: Point, *args, **kwargs
    ) -> Generator[simpy.Event, Any, None]:
        """
        从当前位置移动到下一个相邻的位置
        """
        pass

    @abstractmethod
    def move(
        self, target: Point, speed: Optional[Union[float, Speed]] = None, **kwargs
    ) -> Generator[simpy.Event, Any, None]:
        """
        从当前位置移动到目标位置，此方法是最顶层的移动方法，内部处理路径规划并逐步调用do_move
        TODO: 考虑将speed等参数作为agent的内部属性，而不是在这里传参
        """
        pass

    @property
    def speed_3d(self) -> Optional[ThreeDimensionalVelocity]:
        """
        智能体的3维速度
        """
        raise NotImplementedError(f"{self}未实现3维速度属性")

    def get_moving_duration(
        self, distance: Union[Point], speed: ThreeDimensionalVelocity, **kwargs
    ) -> Time:
        """
        计算移动时间

        Args:
            distance (Union[Point]): 移动距离，三维表示
            speed (ThreeDimensionalVelocity): 移动速度，三维表示

        Returns:
            Time: 移动时间
        """
        raise NotImplementedError(f"{self}未实现get_moving_duration方法")


AgentClass = TypeVar("AgentClass", bound=IAgent)
