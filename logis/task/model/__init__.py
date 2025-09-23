from abc import ABCMeta, abstractmethod
from typing import Iterable, Iterator, Literal, TypeAlias

from networkx import DiGraph
from pydantic import BaseModel, Field

TaskId: TypeAlias = str | int
TaskStatus = Literal["started", "finished", "cancelled", "failed"]


class ITask(metaclass=ABCMeta):
    """
    任务基础抽象类
    """

    @abstractmethod
    def get_task_id(self) -> TaskId:
        pass


TaskLike: TypeAlias = ITask | TaskId


class AbstractTaskManager(metaclass=ABCMeta):
    """
    任务管理器基础抽象类
    """

    @abstractmethod
    def add_task(self, task: TaskLike, parent: TaskLike | None = None, **attr):
        pass

    @abstractmethod
    def add_task_if_absent(self, task: TaskLike, **attr) -> bool:
        pass

    @abstractmethod
    def remove_task(self, task: TaskLike):
        pass

    @abstractmethod
    def remove_task_if_present(self, task: TaskLike):
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

    def get_task_id(self) -> TaskId:
        return self.id


class TaskGraph(AbstractTaskManager):
    """
    以任务id作为节点id组成的任务树
    """

    def __init__(self, **attr):
        self.__graph__ = DiGraph()

    def parse_task_id(self, task: TaskLike) -> TaskId:
        return task.get_task_id() if isinstance(task, ITask) else task

    def get_task(self, task_id: TaskId) -> ITask | None:
        """
        根据任务ID获取任务本身
        """
        node = self.__graph__.nodes.get(task_id)
        return node.get("task") if node else None

    def find_by(self):
        raise NotImplementedError("TaskGraph.find_by not implemented")

    def add_task(self, task: TaskLike, parent: TaskLike | None = None, **attr):
        """
        添加任务

        Args:
            task (TaskLike): 任务对象
            parent (TaskLike | None): 父任务对象. Defaults to None.
        """
        task_id = self.parse_task_id(task)
        self.__graph__.add_node(task_id, task=task, **attr)
        if parent:
            parent_id = self.parse_task_id(parent)
            self.add_task_if_absent(parent)
            self.__graph__.add_edge(parent_id, task_id)

    def add_task_if_absent(
        self, task: TaskLike, parent: TaskLike | None = None, **attr
    ) -> bool:
        """
        只有任务不存在的时候才增加
        """
        task_id = self.parse_task_id(task)
        has = self.__graph__.has_node(task_id)
        if not has:
            self.add_task(task, parent=parent, **attr)
        return has

    def remove_task(self, task: TaskLike):
        """
        删除任务
        """
        task_id = self.parse_task_id(task)
        self.__graph__.remove_node(task_id)

    def remove_task_if_present(self, task: TaskLike) -> bool:
        """
        如果任务存在则删除
        """
        task_id = self.parse_task_id(task)
        has = self.__graph__.has_node(task_id)
        if has:
            self.remove_task(task_id)
        return has

    def get_children_id(self, task: TaskLike) -> Iterator[TaskId]:
        """
        获取任务的所有子任务ID
        """
        return self.__graph__.successors(self.parse_task_id(task))

    def get_parent_id(self, task: TaskLike) -> TaskId | None:
        """
        获取任务的父任务ID
        """
        parents = self.__graph__.predecessors(self.parse_task_id(task))
        return next(parents, None)

    def __contains__(self, task: TaskLike) -> bool:
        """
        检查任务是否存在
        """
        return self.__graph__.has_node(self.parse_task_id(task))
