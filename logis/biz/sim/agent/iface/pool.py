import logging
from abc import ABC, abstractmethod
from collections import defaultdict
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    Generator,
    List,
    Optional,
    Type,
    TypeVar,
    Union,
)

import simpy
from ipa.decorator import deprecated

from logis.biz.sim import AgentId
from logis.biz.sim.const import AgentSelectionStrategyName

from .base import AgentClass, IAgent, Speed, ThreeDimensionalVelocity

if TYPE_CHECKING:
    from ..model import AgentManifest, TaskType

T = TypeVar("T")
from logis.iface import Interface


class IAgentPool(Interface):
    """
    智能体资源池，生命周期钩子如下：
    1. 初始化资源池
    2. 在申请资源之前
    3. 申请资源
    4. 在资源申请到之后
    5. 在资源释放之前
    6. 释放资源
    7. 在资源释放之后

    TODO: 继承自ITaskHandler
    """

    @property
    def get_queue(self):
        """
        获取智能体的请求队列
        """
        if self.use_simpy_store:
            return self.__store__.get_queue
        return []

    @property
    def put_queue(self):
        """
        释放智能体的请求队列
        """
        if self.use_simpy_store:
            return self.__store__.put_queue
        return []

    @property
    @abstractmethod
    def env(self) -> simpy.Environment:
        """
        仿真环境实例
        """
        pass

    @property
    @abstractmethod
    def item_type_id(self) -> Optional[str]:
        """
        池内资源（智能体）的类型 ID

        Returns:
            Optional[str]: 智能体类型 ID
        """
        pass

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.capacity: Optional[int] = None
        """资源池容量"""
        self.speed: Union[Speed, ThreeDimensionalVelocity, None] = None
        """资源池速度"""

        self.use_simpy_store: bool = False
        """是否使用simpy.Store来模拟资源池"""
        self.__store__: Optional[simpy.FilterStore] = None
        self.__lock__ = simpy.Resource(self.env, 1)
        # 所有资源
        self._all_resources: Dict[AgentId, IAgent] = defaultdict()
        # 使用中的资源，是所有资源的子集，用于记录当前正在使用的资源
        self._locked_resources: Dict[AgentId, IAgent] = defaultdict()

    def init_simpy_store(self):
        """
        初始化simpy资源池
        """
        self.__store__ = simpy.FilterStore(self.env, self.capacity)

    def set_locked(self, resource: AgentClass, **kwargs):
        """
        标记资源为已被锁定

        Args:
            resource: 待标记的资源
            kwargs: 其他参数

        Returns:
            bool: 是否成功标记资源为已被锁定
        """
        self._locked_resources[resource.id] = resource

        return True

    def unset_locked(self, resource: AgentClass, **kwargs):
        """
        取消标记资源为未被锁定

        Args:
            resource: 待取消标记的资源
            kwargs: 其他参数

        Returns:
            bool: 是否成功取消标记资源为未被锁定
        """
        self._locked_resources.pop(resource.id, None)
        return True

    def is_resource_locked(self, resource: AgentClass) -> bool:
        """
        判断资源是否已被锁定

        Args:
            resource: 待判断的资源

        Returns:
            bool: 是否已被锁定
        """
        return resource.id in self._locked_resources

    def cancel_request_resource(self, req: simpy.Event):
        """
        取消申请资源，默认仅实现了use_simpy_store模式

        Args:
            req: 待取消的申请事件
        """
        if self.use_simpy_store:
            self.__store__.get_queue.remove(req)
        else:
            raise NotImplementedError("cancel_request_resource not implemented")

    def cancel_release_resource(self, req: simpy.Event):
        """
        取消释放资源，默认仅实现了use_simpy_store模式

        Args:
            req: 待取消的释放事件
        """
        if self.use_simpy_store:
            self.__store__.put_queue.remove(req)
        else:
            raise NotImplementedError("cancel_release_resource not implemented")

    @property
    def resources(self):
        """
        获取所有的资源列表
        """
        return list(self._all_resources.values())

    @property
    def id_resource_map(self):
        """
        获取智能体id到智能体的映射
        """
        return self._all_resources

    def add_agent(self, agent: IAgent):
        """
        添加智能体到资源池

        Args:
            agent: 智能体

        Raises:
            AssertionError: 如果资源池已满，则无法继续添加智能体

        """
        if self.capacity is not None:
            assert (
                len(self._all_resources) < self.capacity
            ), f"{self}资源池已满{self.capacity}，无法添加资源"
        self._all_resources[agent.id] = agent

        if self.use_simpy_store:
            self.__store__.put(agent)

    def is_type_of(self, t: Type) -> bool:
        """
        判断资源池是否是指定类型的资源

        Args:
            t: 资源类型

        Returns:
            bool: 是否是指定类型的资源
        """
        if not self.resources:
            return False
        return isinstance(self.resources[0], t)

    @property
    def available_quantity(self):
        """
        获取资源池中可用的资源数量
        """
        if self.use_simpy_store:
            lx = len(self.__store__.items) if self.__store__ else 0
            return lx
        else:
            lx = None
        ly = len(self._all_resources) - len(self._locked_resources)
        if lx is not None and lx != ly:
            logging.debug(f"两种方式计算的结果不一致，{lx}!={ly}")
        return ly

    def get_resource_by_id(self, id: AgentId):
        """
        根据智能体id获取智能体

        Args:
            id: 智能体id

        Returns:
            Optional[IAgent]: 智能体
        """
        return self._all_resources.get(id, None)

    def before_request_resource(self, **kwargs):
        """
        资源申请之前的回调
        """
        raise NotImplementedError("before_request_resource not implemented")

    def do_request_resource(
        self, resource_id: Optional[str] = None, **kwargs
    ) -> Generator[simpy.Event, Any, Optional[AgentClass]]:
        """
        真正地执行申请资源

        Args:
            resource_id: 资源id
            kwargs: 其他参数

        Returns:
            Generator[simpy.Event, Any, Optional[IAgent]]: 申请资源生成的生成器
        """
        if self.use_simpy_store:
            assert self.__store__, "未初始化资源池，无法申请资源"
            if resource_id is not None:
                return self.__store__.get(
                    filter=lambda item, rid=resource_id: item.id == rid
                )
            return self.__store__.get()
        else:
            raise NotImplementedError("do_request_resource not implemented")

    @abstractmethod
    def after_resource_requested(self, resource: AgentClass, **kwargs):
        """
        资源申请到之后的回调

        Args:
            resource: 已申请到的资源
        """
        pass

    @abstractmethod
    def request_resource(
        self,
        fast_fail: bool = False,
        resource_id: Optional[str] = None,
        **kwargs,
    ) -> Generator[simpy.Event, Any, Optional[IAgent]]:
        """
        申请资源。此方法是个简单的方法组合（可能并不通用），内部会依次调用：
        1. before_request_resource
        2. do_request_resource
        3. after_resource_requested

        如果不满足您的需求，请自定义`IAgentSelectionStrategy`策略并实现`request`方法

        Args:
            strategy: 智能体选择策略
            fast_fail: 是否快速失败，如果为True，当资源池中没有可用资源时，直接返回None
            resource_id: 资源id
            kwargs: 其他参数

        Returns:
            智能体事件生成器
        """

        if fast_fail and self.available_quantity <= 0:
            return None

        self.before_request_resource(**kwargs)
        try:
            req = self.do_request_resource(resource_id=resource_id)
            resource: Optional["IAgent"] = yield req
        except simpy.Interrupt:
            self.cancel_request_resource(req)
            resource = None

        if resource:
            self.after_resource_requested(resource=resource, **kwargs)
        return resource

    def before_release_resource(self, resource: AgentClass, **kwargs):
        """
        资源释放之前的回调

        Args:
            resource: 待释放的资源
        """
        raise NotImplementedError("before_release_resource not implemented")

    def do_release_resource(self, resource: AgentClass, **kwargs):
        """
        真正地执行释放资源

        Args:
            resource: 待释放的资源
        """
        if self.use_simpy_store:
            assert self.__store__, "未初始化资源池，无法释放资源"
            return self.__store__.put(resource)
        else:
            raise NotImplementedError("do_release_resource not implemented")

    def after_resource_released(self, resource: AgentClass, **kwargs):
        """
        资源释放之后的回调

        Args:
            resource: 已释放的资源
        """
        raise NotImplementedError("after_resource_released not implemented")

    @abstractmethod
    def release_resource(self, resource: AgentClass, *args, **kwargs):
        """
        释放资源。此方法是个简单的方法组合（可能并不通用），内部会依次调用：
        1. before_release_resource
        2. do_release_resource
        3. after_resource_released

        如果不满足您的需求，请自定义`IAgentSelectionStrategy`策略并实现`release`方法

        Args:
            resource: 要释放的资源
            kwargs: 其他参数
        """

        agent_pool = self
        agent_pool.before_release_resource(resource=resource, **kwargs)
        e = agent_pool.do_release_resource(resource=resource)
        # TODO: 这里是否不等待就可以
        yield e
        agent_pool.after_resource_released(resource=resource, **kwargs)
        return True

    @abstractmethod
    def assign_resources(
        self, task_type: str, task_keys: List[T], **kwargs
    ) -> Generator[
        simpy.Event, Any, Dict[AgentId, "AgentManifest[AgentClass, TaskType]"]
    ]:
        """
        输入任务分配智能体

        Args:
            task_type: 任务类型
            task_keys: 任务key列表
            kwargs: 其他参数

        Returns:
            智能体id到智能体manifest的映射
        """
