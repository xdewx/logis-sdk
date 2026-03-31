from abc import ABC, abstractmethod
from typing import List, Optional

from logis.biz.sim.ctx import Context
from logis.biz.sim.iface import IExpose

from .base import IAgent
from .pool import IAgentPool


class IAgentSelectionStrategy(IExpose):
    """
    智能体选择策略
    """

    def __init__(self, agent_pool: Optional[IAgentPool] = None, **kwargs) -> None:
        super().__init__(**kwargs)
        self.agent_pool = agent_pool

    @abstractmethod
    def select_agent(
        self, agent_pool: Optional[IAgentPool] = None, **kwargs
    ) -> Optional[IAgent]:
        """
        选择符合需求的智能体
        """


class DefaultAgentSelectionStrategy(IAgentSelectionStrategy):
    """
    默认智能体选择策略
    """

    def select_agent(self, agent_pool: Optional[IAgentPool] = None, **kwargs):
        """
        选择所有智能体
        """
        agent_pool = agent_pool or self.agent_pool
        assert agent_pool, "未指定资源池，无法申请资源"
        agent = yield from agent_pool.request_resource(**kwargs)
        return agent
