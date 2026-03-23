import heapq
import math
from collections import defaultdict
from typing import Callable, Dict, List, Optional, Set, Tuple

from logis.data_type import Point
from logis.math import euclid_distance

from .base import A_STAR_ALGORITHM, PathFindingAlgorithm, track_path
from .model import PathFindingInput, PathFindingOutput


def a_star(
    starter: Point,
    ender: Point,
    nb_dis_dic: Dict[
        Point, List[Tuple[Point, float]]
    ],  # 每个点的邻居点和距离和所需要的速度以及该点的角速度
    heuristic_func: Callable[[Point, Point], float] = None,
    excluded_vertices: List[Point] = [],
    input: Optional[PathFindingInput] = None,
):
    """
    在图中使用 A* 算法寻找从起始点到终点的路径。

    参数:
        starter (Point): 起始点。
        ender (Point): 终点。
        nb_dis_dic (Dict[Point, List[Tuple[Point, float, float, float]]]):
            字典，键为顶点，值为元组列表，元组包含 (邻居顶点, 距离, 速度, 角速度)。
        heuristic_func (Callable[[Point, Point], float], 可选):
            启发式函数，接受两个顶点并返回启发式距离。默认为欧几里得距离。
        excluded_vertices (List[Point], 可选): 要排除的顶点列表。默认为空列表。

    返回:
        Tuple[bool, List[Point], List[float], List[float]]:
            若找到路径，返回 (True, 路径列表, 速度列表, 转向时间列表)；
            若未找到路径，返回 (False, None, [], [])。
    """

    if starter == ender:
        return PathFindingOutput(success=True, paths=[[starter]])

    # If no heuristic function is provided, use Euclidean distance as default
    if heuristic_func is None:
        heuristic_func = euclid_distance

    # Priority queue to store the vertices to be explored
    frontier: List[Tuple[float, float, Point]] = []
    heapq.heappush(frontier, (0, 0, starter))  # (current_cost, heuristic_cost, vertex)

    came_from: Dict[Point, List[Point]] = defaultdict(list)
    # Dictionary to store the cost of getting to each vertex
    cost_so_far = {starter: 0}
    # 用于记录到达每个顶点所经过边的速度
    speed_so_far = {starter: None}
    # 用于记录到达每个顶点所经过边的角速度
    angular_speed_so_far = {starter: None}
    # 用于记录到达每个顶点时的前一个顶点，用于计算转向
    prev_vertex = {starter: None}
    # Set to keep track of visited vertices
    visited: Set[Point] = set()
    success = False
    while frontier:
        _, _, current = heapq.heappop(frontier)

        if current == ender:
            success = True
            break

        visited.add(current)

        for neighbor, weight in nb_dis_dic[current]:
            if neighbor in excluded_vertices:
                continue
            # 如果节点已经被处理过就不再处理
            if neighbor in visited:
                continue
            # TODO:如果节点已经在待处理队列中就跳过?
            if neighbor in [vertex[2] for vertex in frontier]:
                continue
            new_cost = cost_so_far[current] + weight
            # 如果新路径更长就跳过
            old_cost = cost_so_far.get(neighbor, math.inf)
            if new_cost > old_cost:
                continue

            # 注释掉下面的判断可以生成多条路径
            # # 如果达到neighbor的成本相同，就只选择第一次选中的那个，从而避免产生多条等长的路径
            if new_cost == old_cost:
                continue

            if new_cost < old_cost:
                came_from[neighbor].clear()

            cost_so_far[neighbor] = new_cost
            priority = new_cost + heuristic_func(neighbor, ender)
            heapq.heappush(frontier, (priority, new_cost, neighbor))
            came_from[neighbor].append(current)

    # 创建正向连接关系方便后续遍历
    step_into: Dict[Point, List[Point]] = defaultdict(list)
    for target, sources in came_from.items():
        for source in sources:
            step_into[source].append(target)

    # 如果找到了起点到终点的路径就剪枝回溯
    if success:
        assert ender in came_from, "寻路算法出错了"
        step_into.clear()
        targets = [ender]
        while targets:
            target = targets.pop()
            sources = came_from.get(target, [])
            for source in sources:
                step_into[source].append(target)
            targets.extend(sources)

    if not success:
        return PathFindingOutput(success=False, paths=[])

    # 如果没找到直接到终点的路线，就尝试找一个最接近终点的点
    paths = track_path(step_into, starter, ender, limit=None if success else 1)
    paths = list(
        filter(lambda p: len(p) > (1 if p[0] in [starter, ender] else 0), paths)
    )
    return PathFindingOutput(success=success, paths=paths)


class AStarPathFinding(PathFindingAlgorithm):
    """
    A*寻路算法实现
    """

    type = A_STAR_ALGORITHM

    def find_path(self, input: PathFindingInput, **kwargs) -> PathFindingOutput:
        """
        使用A*算法寻找从start到end的路径
        """
        return a_star(
            input=input,
            starter=input.start,
            ender=input.end,
            nb_dis_dic=input.distance_matrix,
            heuristic_func=input.heuristic_func,
            excluded_vertices=set(input.excluded_vertices),
            **kwargs,
        )
