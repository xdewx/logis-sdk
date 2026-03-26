from typing import Generic, Iterable, Iterator, Optional, TypeAlias, TypeVar, Union

from pydantic import BaseModel

from logis.biz.sim import AgentId
from logis.data_type import DEFAULT_PYDANTIC_MODEL_CONFIG

from ..iface import AgentClass

TaskType = TypeVar("TaskType")


class AgentManifest(BaseModel, Generic[AgentClass, TaskType]):
    agent: Optional[AgentClass] = None
    agent_id: Optional[AgentId] = None

    tasks: Union[Iterable[TaskType], Iterator[TaskType]] = []

    __task_iter__: Optional[Iterator[TaskType]] = None

    def get_task_iter(self, is_new: bool = False):
        if is_new or self.__task_iter__ is None:
            self.__task_iter__ = iter(self.tasks)
        return self.__task_iter__

    model_config = DEFAULT_PYDANTIC_MODEL_CONFIG
