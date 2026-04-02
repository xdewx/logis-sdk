from abc import ABC, abstractmethod
from typing import List, Optional

import simpy

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
    def request(
        self, agent_pool: Optional[IAgentPool] = None, fast_fail: bool = False, **kwargs
    ) -> Optional[IAgent]:
        """
        选择符合需求的智能体
        """

    def release(self, agent: IAgent, agent_pool: Optional[IAgentPool] = None, **kwargs):
        """
        释放智能体
        """
        agent_pool = agent_pool or self.agent_pool
        assert agent_pool, "未指定资源池，无法释放资源"
        agent_pool.before_release_resource(resource=agent, **kwargs)
        e = agent_pool.do_release_resource(resource=agent)
        # TODO: 这里是否不等待就可以
        yield e
        agent_pool.after_resource_released(resource=agent, **kwargs)
        return True


class DefaultAgentSelectionStrategy(IAgentSelectionStrategy):
    """
    默认智能体选择策略
    """

    def request(
        self, agent_pool: Optional[IAgentPool] = None, fast_fail: bool = False, **kwargs
    ):
        """
        选择所有智能体
        """
        agent_pool = agent_pool or self.agent_pool
        assert agent_pool, "未指定资源池，无法申请资源"

        if fast_fail and agent_pool.available_quantity <= 0:
            return None

        try:
            req = agent_pool.do_request_resource()
            resource: Optional["IAgent"] = yield req
        except simpy.Interrupt:
            agent_pool.cancel_request_resource(req)
            resource = None

        if resource:
            agent_pool.after_resource_requested(resource=resource, **kwargs)
        return resource
