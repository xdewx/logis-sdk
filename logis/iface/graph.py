from abc import ABC, abstractmethod
from typing import Generic, List, TypeVar


class INode(ABC):
    pass


class IEdge(ABC):

    @abstractmethod
    def get_weight(self, *args, **kwargs) -> float:
        """
        获取边的权重
        """
        pass

    @abstractmethod
    def is_directed(self) -> bool:
        """
        是否有向边
        """
        pass


E = TypeVar("E", bound=IEdge)
V = TypeVar("V")


class IPathGraph(ABC, Generic[E, V]):
    """
    路径关系图
    """

    @property
    @abstractmethod
    def edges(self) -> List[E]:
        """
        所有的边
        """
        pass

    @property
    @abstractmethod
    def nodes(self) -> List[V]:
        """
        所有的节点
        """
        pass
