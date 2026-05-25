from typing import Generic, Iterable, Iterator, Optional, TypeAlias, TypeVar, Union

from pydantic import BaseModel

from logis.biz.sim import AgentId
from logis.data_type import DEFAULT_PYDANTIC_MODEL_CONFIG

from ..iface import AgentClass

TaskType = TypeVar("TaskType")


class AgentManifest(BaseModel, Generic[AgentClass, TaskType]):
    """
    智能体的任务清单
    """

    agent: Optional[AgentClass] = None
    """智能体实例"""
    agent_id: Optional[AgentId] = None
    """智能体实例ID"""

    tasks: Union[Iterable[TaskType], Iterator[TaskType]] = []
    """任务列表"""

    __task_iter__: Optional[Iterator[TaskType]] = None

    def get_task_iter(self, is_new: bool = False) -> Iterator[TaskType]:
        """
        获取任务迭代器

        Args:
            is_new (bool, optional): 是否重新获取迭代器. Defaults to False.

        Returns:
            Iterator[TaskType]: 任务迭代器
        """
        if is_new or self.__task_iter__ is None:
            self.__task_iter__ = iter(self.tasks)
        return self.__task_iter__

    model_config = DEFAULT_PYDANTIC_MODEL_CONFIG
