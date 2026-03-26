from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Dict, Generator, List, Optional, TypeVar

import simpy

from logis.biz.sim import AgentId

from .base import AgentClass, IAgent

if TYPE_CHECKING:
    from ..model import AgentManifest, TaskType

T = TypeVar("T")


class IAgentPool(ABC):
    """
    TODO: 继承自ITaskHandler
    """

    @property
    def resources(self) -> List[IAgent]:
        """
        获取所有的智能体列表
        """
        pass

    def get_resource_by_id(self, id: AgentId) -> Optional[AgentClass]:
        """
        根据智能体id获取智能体
        """
        for r in self.resources:
            if r.id == id:
                return r
        return None

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
