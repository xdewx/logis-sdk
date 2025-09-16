from abc import ABCMeta, abstractmethod
from typing import Iterable, Literal, TypeAlias

from networkx import DiGraph
from pydantic import BaseModel, Field

TaskId: TypeAlias = str | int
TaskStatus = Literal[""]


class ITask(metaclass=ABCMeta):
    """
    任务基础抽象类
    """

    @property
    @abstractmethod
    def id(self) -> TaskId:
        pass


class Task(BaseModel, ITask):
    """
    任务基础结构
    """

    id: TaskId | None = None
    parent_id: TaskId | None = None
    children_ids: Iterable[TaskId] = Field(default_factory=list)

    name: str | None = None
    type: str | None = None
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


class TaskGraph(DiGraph):
    """
    以任务id作为节点id组成的任务树
    """

    def find_by_id(self, task_id: TaskId) -> ITask | None:
        """
        根据任务ID获取任务本身
        """
        node = self.nodes.get(task_id)
        return node["task"] if node else None

    def find_by(self):
        pass

    def add_task(self, task: ITask, **attr):
        self.add_node(task.id, task=task, **attr)

    def add_task_if_absent(self, task: ITask, **attr):
        """
        只有节点不存在的时候才增加
        """
        has = self.has_node(task.id)
        if not has:
            self.add_task(task, **attr)
        return has
