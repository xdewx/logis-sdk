from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Dict, Generator, List, Optional, TypeVar

import simpy

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

    def __init__(self, *args, **kwargs) -> None:
        super().__init__()
        self.capacity: Optional[int] = None
        self._store: Optional[simpy.Store] = None

    def cancel_request_resource(self, req: simpy.Event):
        """
        取消申请资源
        """
        self._store.get_queue.remove(req)

    def cancel_release_resource(self, req: simpy.Event):
        """
        取消释放资源
        """
        self._store.put_queue.remove(req)

    def do_request_resource(
        self, **kwargs
    ) -> Generator[simpy.Event, Any, Optional[AgentClass]]:
        """
        执行申请资源
        """
        assert self._store, "未初始化资源池，无法申请资源"
        return self._store.get()

    def do_release_resource(self, resource: AgentClass, *args, **kwargs):
        """
        执行释放资源
        """
        assert self._store, "未初始化资源池，无法释放资源"
        return self._store.put(resource)

    @property
    def resources(self) -> List[IAgent]:
        """
        获取所有的智能体列表
        """
        pass

    @property
    def available_quantity(self):
        return len(self._store.items)

    def get_resource_by_id(self, id: AgentId) -> Optional[AgentClass]:
        """
        根据智能体id获取智能体
        """
        for r in self.resources:
            if r.id == id:
                return r
        return None

    def before_request_resource(self, **kwargs):
        """
        资源申请之前的回调
        """
        raise NotImplementedError()

    @abstractmethod
    def request_resource(
        self,
        *args,
        strategy: Optional[AgentSelectionStrategyName] = None,
        fast_fail: bool = False,
        **kwargs
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
        raise NotImplementedError()

    @abstractmethod
    def release_resource(self, resource: AgentClass, *args, **kwargs):
        """
        释放资源
        """

    def after_resource_released(self, **kwargs):
        """
        资源释放之后的回调
        """
        raise NotImplementedError()

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
