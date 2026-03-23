from typing import Any, Callable, Dict, List, Optional, Tuple, Union

from networkx import DiGraph, Graph
from pydantic import BaseModel, Field

from logis.data_type import DEFAULT_PYDANTIC_MODEL_CONFIG, Point, Predicate

from ..base import Path, PathFindingAlgorithmType


class PathFindingConfig(BaseModel):
    obstacle_filter: Optional[Predicate[Any]] = None


class PathFindingInput(BaseModel):
    # 算法名称，分流用
    alg: Union[PathFindingAlgorithmType, str, None] = None

    # 图对象，可以是无向图或有向图
    graph: Union[Graph, DiGraph, None] = None

    # 起点
    start: Point
    # 终点
    end: Point

    # 点到点的距离矩阵
    # TODO: 从graph中获取
    distance_matrix: Dict[Point, List[Tuple[Point, float]]] = Field(
        default_factory=dict
    )
    # 排除的点或障碍点
    excluded_vertices: List[Point] = []

    # 启发式距离计算方法
    heuristic_func: Callable[[Point, Point], float] = None

    model_config = DEFAULT_PYDANTIC_MODEL_CONFIG

class PathFindingOutput(BaseModel):
    """
    寻路输出结果
    可以输出具体路径，也可以只输出下一点
    """

    # 是否成功
    success: bool

    # 具体路径的速度
    speeds: Optional[List[float]] = None

    # 可能存在多条路径
    paths: Optional[List[Path]] = None

    # 具体路径
    path: Optional[List[Point]] = None

    next_point: Optional[Point] = None

    model_config = DEFAULT_PYDANTIC_MODEL_CONFIG
