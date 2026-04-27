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
        """
        初始化智能体选择策略

        Args:
            agent_pool: 智能体池
            kwargs: 其他参数
        """
        super().__init__(**kwargs)
        self.agent_pool = agent_pool

    @abstractmethod
    def request(
        self, agent_pool: Optional[IAgentPool] = None, fast_fail: bool = False, **kwargs
    ) -> Optional[IAgent]:
        """
        选择符合需求的智能体

        Args:
            agent_pool: 智能体池，如果不传，默认使用初始化时指定的智能体池
            fast_fail: 是否快速失败，如果为True，且当前智能体池没有可用智能体，则直接返回None
            kwargs: 其他参数

        Returns:
            Optional[IAgent]: 符合需求的智能体
        """

    def release(self, agent: IAgent, agent_pool: Optional[IAgentPool] = None, **kwargs):
        """
        释放智能体

        Args:
            agent: 智能体
            agent_pool: 智能体池，如果不传，默认使用初始化时指定的智能体池
            kwargs: 其他参数

        Returns:
            bool: 是否成功释放智能体
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
