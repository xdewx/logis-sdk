import logging
from abc import ABC, abstractmethod
from collections import defaultdict
from typing import TYPE_CHECKING, Any, Dict, Generator, List, Optional, Type, TypeVar

import simpy
from ipa.decorator import deprecated

from logis.biz.sim import AgentId
from logis.biz.sim.const import AgentSelectionStrategyName

from .base import AgentClass, IAgent

if TYPE_CHECKING:
    from ..model import AgentManifest, TaskType

T = TypeVar("T")


class IAgentPool(ABC):
    """
    TODO: 继承自ITaskHandler
    """

    @property
    def get_queue(self):
        if self.use_simpy_store:
            return self.__store__.get_queue
        return []

    @property
    def put_queue(self):
        if self.use_simpy_store:
            return self.__store__.put_queue
        return []

    @property
    @abstractmethod
    def env(self) -> simpy.Environment:
        pass

    def __init__(self, *args, **kwargs) -> None:
        super().__init__()
        self.capacity: Optional[int] = None

        self.use_simpy_store: bool = False
        self.__store__: Optional[simpy.Store] = None
        self.__lock__ = simpy.Resource(self.env, 1)
        # 所有资源
        self._all_resources: Dict[AgentId, IAgent] = defaultdict()
        # 使用中的资源，是所有资源的子集，用于记录当前正在使用的资源
        self._locked_resources: Dict[AgentId, IAgent] = defaultdict()

    def init_simpy_store(self):
        """
        初始化simpy资源池
        """
        self.__store__ = simpy.Store(self.env, self.capacity)

    def set_locked(self, resource: AgentClass, **kwargs):
        """
        标记资源为已被锁定
        """
        self._locked_resources[resource.id] = resource

    def unset_locked(self, resource: AgentClass, **kwargs):
        """
        取消标记资源为未被锁定
        """
        self._locked_resources.pop(resource.id, None)

    def is_locked(self, resource: AgentClass) -> bool:
        """
        判断资源是否已被锁定
        """
        return resource.id in self._locked_resources

    def cancel_request_resource(self, req: simpy.Event):
        """
        取消申请资源
        """
        if self.use_simpy_store:
            self.__store__.get_queue.remove(req)
        else:
            raise NotImplementedError("cancel_request_resource not implemented")

    def cancel_release_resource(self, req: simpy.Event):
        """
        取消释放资源
        """
        if self.use_simpy_store:
            self.__store__.put_queue.remove(req)
        else:
            raise NotImplementedError("cancel_release_resource not implemented")

    def do_request_resource(
        self, **kwargs
    ) -> Generator[simpy.Event, Any, Optional[AgentClass]]:
        """
        执行申请资源
        """
        if self.use_simpy_store:
            assert self.__store__, "未初始化资源池，无法申请资源"
            return self.__store__.get()
        else:
            raise NotImplementedError("do_request_resource not implemented")

    def do_release_resource(self, resource: AgentClass, *args, **kwargs):
        """
        执行释放资源
        """
        if self.use_simpy_store:
            assert self.__store__, "未初始化资源池，无法释放资源"
            return self.__store__.put(resource)
        else:
            raise NotImplementedError("do_release_resource not implemented")

    @property
    def resources(self):
        """
        获取所有的资源列表
        """
        return list(self._all_resources.values())

    @property
    def id_resource_map(self):
        return self._all_resources

    def add_agent(self, agent: IAgent):
        """
        添加智能体到资源池
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
            lx = len(self.__store__.items) if self.__store__ else None
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
        """
        return self._all_resources.get(id, None)

    def before_request_resource(self, **kwargs):
        """
        资源申请之前的回调
        """
        raise NotImplementedError("before_request_resource not implemented")

    @deprecated("使用AgentSelectionStrategy.request")
    @abstractmethod
    def request_resource(
        self,
        *args,
        strategy: Optional[AgentSelectionStrategyName] = None,
        fast_fail: bool = False,
        **kwargs,
    ) -> Generator[simpy.Event, Any, Optional[IAgent]]:
        """
        申请资源
        """

    @abstractmethod
    def after_resource_requested(self, **kwargs):
        """
        资源申请到之后的回调
        """
        pass

    def before_release_resource(self, **kwargs):
        """
        资源释放之前的回调
        """
        raise NotImplementedError("before_release_resource not implemented")

    @deprecated("使用AgentSelectionStrategy.release")
    @abstractmethod
    def release_resource(self, resource: AgentClass, *args, **kwargs):
        """
        释放资源
        """

    def after_resource_released(self, **kwargs):
        """
        资源释放之后的回调
        """
        raise NotImplementedError("after_resource_released not implemented")

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
