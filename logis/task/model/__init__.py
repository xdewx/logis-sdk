from abc import ABCMeta, abstractmethod
from typing import Iterable, Literal, TypeAlias

from pydantic import BaseModel, Field

TaskId: TypeAlias = str | int
TaskStatus = Literal["started", "finished", "cancelled", "failed"]
TaskPriority: TypeAlias = str | int


class ITask(metaclass=ABCMeta):
    """
    任务基础抽象类
    """

    @abstractmethod
    def get_task_id(self) -> TaskId:
        pass

    @abstractmethod
    def get_priority(self) -> TaskPriority:
        """
        任务优先级
        """
        pass

    # @abstractmethod
    # def get_status(self) -> TaskStatus:
    #     pass


TaskLike: TypeAlias = ITask | TaskId


class Task(BaseModel, ITask):
    """
    任务基础结构
    """

    id: TaskId | None = None
    parent_id: TaskId | None = None
    children_ids: Iterable[TaskId] = Field(default_factory=list)

    name: str | None = None
    type: str | None = None
    priority: TaskPriority | None = None

    repeat: int = 1
    progress: float | int = 0
    tags: Iterable[str] = Field(default_factory=set)

    created_at: int | None = None
    updated_at: int | None = None
    started_at: int | None = None
    finished_at: int | None = None
    cancelled_at: int | None = None

    status: TaskStatus | None = None

    remark: str | None = None

    def get_task_id(self) -> TaskId:
        return self.id

    def get_priority(self) -> TaskPriority:
        return self.priority
