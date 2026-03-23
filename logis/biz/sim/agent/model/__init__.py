from typing import Generic, Iterable, Iterator, Optional, TypeVar, Union

from pydantic import BaseModel

from logis.data_type import DEFAULT_PYDANTIC_MODEL_CONFIG

TaskType = TypeVar("TaskType")
AgentType = TypeVar("AgentType")


class AgentManifest(BaseModel, Generic[AgentType, TaskType]):
    agent: Optional[AgentType] = None
    agent_id: Optional[Union[int, str]] = None

    tasks: Union[Iterable[TaskType], Iterator[TaskType]] = []

    __task_iter__: Optional[Iterator[TaskType]] = None

    def get_task_iter(self, is_new: bool = False):
        if is_new or self.__task_iter__ is None:
            self.__task_iter__ = iter(self.tasks)
        return self.__task_iter__

    model_config = DEFAULT_PYDANTIC_MODEL_CONFIG
