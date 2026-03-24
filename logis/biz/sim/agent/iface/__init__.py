from abc import abstractmethod
from typing import Any, Generator, Optional, TypeVar, Union

import simpy

from logis.biz.sim import IBlueprint
from logis.biz.sim.graph import IPathGraph
from logis.biz.sim.transport import ITransport
from logis.data_type import Point, Speed


class IAgent(ITransport, IBlueprint):

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
        self,
        target: Point,
        speed: Optional[Union[float, Speed]] = None,
        agent_as_obstacle: bool = False,
        rack_as_obstacle: bool = False,
        **kwargs
    ) -> Generator[simpy.Event, Any, None]:
        """
        从当前位置移动到目标位置，此方法是最顶层的移动方法，内部处理路径规划并逐步调用do_move
        """
        pass


AgentClass = TypeVar("AgentClass", bound=IAgent)
