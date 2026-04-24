from abc import abstractmethod
from collections import defaultdict
from typing import TYPE_CHECKING, Dict, List, Optional, Set, Tuple

import simpy
from networkx import DiGraph

from logis.alg.path_finding import PathFindingAlgorithm, PathFindingOutput
from logis.data_type import Point
from logis.iface.graph import IPathGraph

from ..model import DirEdge

if TYPE_CHECKING:
    from logis.biz.sim.transport import ObstacleDetectorConfig

class ISimPathGraph(IPathGraph[DirEdge, Point]):
    """
    路径关系图
    """

    @property
    @abstractmethod
    def env(self) -> simpy.Environment:
        pass

    def __init__(self, *args, **kwargs) -> None:
        super().__init__()
        # TODO: 是否直接继承会更方便？
        self._graph_ = DiGraph()
        self._lock_nodes_map: Dict[str, Set[Point]] = defaultdict(lambda: set())
        self._path_lock = simpy.Resource(self.env)
        self.__index_point_map__: Dict[str, Point] = {}

    def request_path_lock(self):
        return self._path_lock.request()

    def nodes(self, *args, **kwargs) -> List[Point]:
        return list(self._graph_.nodes(*args, **kwargs))

    def edges(self, *args, **kwargs) -> List[DirEdge]:
        return list(self._graph_.edges(*args, **kwargs))

    def lock_node(self, lock_id: str, node: Point):
        self._lock_nodes_map[lock_id].add(node)

    def unlock_node(self, lock_id: str, node: Point):
        if node in self._lock_nodes_map[lock_id]:
            self._lock_nodes_map[lock_id].remove(node)

    def unlock_nodes_by_lock_id(self, lock_id: str):
        self._lock_nodes_map[lock_id].clear()

    def get_locked_by_other(self, my_lock_id: str):
        return set().union(
            *[nodes for id, nodes in self._lock_nodes_map.items() if id != my_lock_id]
        )

    def lock_path(self, lock_id: str, path: List[Point], limit: Optional[int] = None):
        """
        锁格
        """
        path = path[0:limit]
        while True:
            with self.request_path_lock() as req:
                yield req
                locked = self.get_locked_by_other(lock_id)
                if len(locked.intersection(path)) == 0:
                    # 在获取锁的情况下立即锁定路径
                    for p in path:
                        self._lock_nodes_map[lock_id].add(p)
                    break
            # 未获取锁或路径被锁定，等待后重试
            yield self.env.timeout(0.5)

    def unlock_path(self, lock_id: str, path: List[Point]):
        for p in path:
            if p in self._lock_nodes_map[lock_id]:
                self._lock_nodes_map[lock_id].remove(p)

    def add_nodes(self, *nodes: Point):
        for node in nodes:
            self._graph_.add_node(node)

    def add_edges(self, *edges: DirEdge):
        for edge in edges:
            self._graph_.add_edge(edge.starter, edge.ender, weight=edge.get_weight())

    def remove_edges(self, *edges: DirEdge):
        for edge in edges:
            self._graph_.remove_edge(edge.starter, edge.ender)

    def remove_edges_if_exists(self, *edges: DirEdge):
        for edge in edges:
            if edge.starter in self._graph_ and edge.ender in self._graph_:
                self._graph_.remove_edge(edge.starter, edge.ender)

    def get_index_point_map(self, init: bool = False, **kwargs):
        """
        获取索引点映射

        Args:
            init: 是否强制重新初始化映射，默认False

        Returns:
            Dict[str, Point]
        """
        return self.__index_point_map__

    def get_point_by_index(self, index: str):
        return self.__index_point_map__.get(index)

    def realtime_obstacles(
        self, my_lock_id: str, config: "ObstacleDetectorConfig", **kwargs
    ) -> Tuple[List[Point], List[Point]]:
        """
        实时获取障碍物

        Args:
            my_lock_id: 获取方的锁ID
            config: 障碍物检测配置
            **kwargs: 其他参数

        Returns:
            Tuple[List[Point], List[Point]]: (智能体障碍物点列表, 所有障碍物点列表)
        """
        raise NotImplementedError("realtime_obstacles not implemented")

    @abstractmethod
    def find_path(
        self,
        src: Point,
        dest: Point,
        alg: PathFindingAlgorithm,
        excluded_vertices: List[Point] = [],
        **kwargs,
    ) -> PathFindingOutput:
        """
        路径规划

        TODO: 后续把图作为参数传入算法，而不是把算法作为参数传入图

        Args:
            src: 起始点
            dest: 目的地
            alg: 路径规划算法，默认AStar算法
            excluded_vertices: 排除的顶点，默认空列表
            **kwargs: 其他参数

        Returns:
            PathFindingOutput: 路径规划结果
        """
