from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Iterable, List, Tuple

from logis.data_type import Point

if TYPE_CHECKING:
    from logis.biz.sim.agent import IAgent
    from logis.biz.sim.storage import IRack


class IGrid(ABC):
    """
    网格
    """

    @property
    @abstractmethod
    def agents(self) -> Iterable["IAgent"]:
        """
        所有的智能体
        """
        pass

    @property
    @abstractmethod
    def racks(self) -> Iterable["IRack"]:
        """
        所有的货架
        """
        pass

    @property
    @abstractmethod
    def points(self) -> Iterable[Point]:
        """
        所有的点
        """
        pass

    @abstractmethod
    def get_point_at(self, i: int, j: int) -> Point:
        """
        根据网格坐标获取点坐标
        """
        pass

    @abstractmethod
    def get_index_of_point(self, point: Point) -> Tuple[int, int]:
        """
        根据点坐标获取网格坐标
        """
        pass

    @abstractmethod
    def get_free_points(self) -> List[Point]:
        """
        获取空闲的点
        """
        pass
