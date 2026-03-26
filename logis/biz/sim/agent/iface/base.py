from abc import ABC, abstractmethod
from typing import Any, Generator, Optional, TypeVar, Union

import simpy

from logis.biz.sim import AgentId, IBlueprint
from logis.biz.sim.transport import ITransport
from logis.data_type import Point, Speed


class IAgent(ITransport, IBlueprint):

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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.origin_location: Optional[Point] = None
        self.current_location: Optional[Point] = None

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


AgentClass = TypeVar("AgentClass", bound=IAgent)
