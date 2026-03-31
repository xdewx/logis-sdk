from abc import ABC, abstractmethod
from typing import Any, Generator, Optional

import simpy

from logis.biz.sim.const import GoHomeStrategyFrequency
from logis.biz.sim.graph import IPathGraph
from logis.biz.sim.iface import IExpose
from logis.data_type.base import Predicate

from .base import *


class AgentIdleStrategy(IExpose):
    """
    智能体空闲策略
    """

    def __init__(self, agent: Optional[AgentClass] = None, **kwargs) -> None:
        """
        初始化智能体空闲策略
        Args:
            agent: 智能体,是否要传取决于此策略是否仅针对此智能体
        """
        super().__init__(**kwargs)
        self.agent = agent

    def is_idle(self, agent: Optional[AgentClass] = None, **kwargs) -> bool:
        """
        判断智能体是否空闲
        """
        raise NotImplementedError("is_idle方法尚未实现")

    @abstractmethod
    def on_idle(
        self,
        agent: Optional[AgentClass] = None,
        is_idle: Optional[Predicate[AgentClass]] = None,
        **kwargs,
    ) -> Generator[simpy.Event, Any, None]:
        """
        智能体做完任务之后的回调逻辑
        Args:
            agent: 如果不传则使用初始化时传的智能体，否则使用传参的智能体
            is_idle: 判断智能体是否空闲的方法，如果不传则使用is_idle方法，否则使用传参的方法判断
        """


class GoHomeStrategy(AgentIdleStrategy):
    """
    回到归属地策略
    """

    def __init__(
        self,
        frequency: GoHomeStrategyFrequency,
        agent: Optional[AgentClass] = None,
        env: Optional[simpy.Environment] = None,
        **kwargs,
    ) -> None:
        super().__init__(agent=agent, **kwargs)
        self.frequency: GoHomeStrategyFrequency = frequency
        self.env: simpy.Environment = env

    def on_idle(
        self,
        agent: Optional[AgentClass] = None,
        is_idle: Optional[Predicate[AgentClass]] = None,
        **kwargs,
    ):
        """
        默认空闲策略，智能体在空闲时，等待下一个任务
        """
        agent = agent or self.agent
        is_idle = is_idle or self.is_idle

        if (
            self.frequency == "如果无其他任务" and is_idle(agent, **kwargs)
        ) or self.frequency == "每次":
            yield from agent.move(target=agent.origin_location, **kwargs)
        else:
            raise NotImplementedError(f"频率{self.frequency}尚未支持")
