from abc import abstractmethod
from collections import defaultdict
from typing import Dict, List, Optional, Set

import simpy
from networkx import DiGraph

from logis.data_type import Point
from logis.iface.graph import IPathGraph

from ..model import DirEdge


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
