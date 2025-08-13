from abc import ABCMeta, abstractmethod
from inspect import isclass
from typing import Any, Callable, Dict, List, NewType, Optional, Tuple, Type, TypeAlias

from networkx import DiGraph, Graph
from pydantic import BaseModel, Field

from logis.conf import PYDANTIC_DEFAULT_MODEL_CONFIG
from logis.types import Point

PathFindingAlgorithmType = NewType("PathFindingAlgorithmType", str)

AlgorithmTypeResolver: TypeAlias = Callable[[Any], PathFindingAlgorithmType]

# TODO: 完善名字、补充类型
A_STAR_ALGORITHM = PathFindingAlgorithmType("a_star")
DIJKSTRA_ALGORITHM = PathFindingAlgorithmType("dijkstra")


class PathFindingInput(BaseModel):
    # 算法名称，分流用
    alg: PathFindingAlgorithmType | str | None = None

    # 图对象，可以是无向图或有向图
    graph: Graph | DiGraph | None = None

    # 起点
    start: Point
    # 终点
    end: Point

    # 排除的点或障碍点
    excluded_vertices: List[Point] = []

    model_config = PYDANTIC_DEFAULT_MODEL_CONFIG


class PathFindingOutput(BaseModel):
    """
    寻路输出结果
    可以输出具体路径，也可以只输出下一点
    """

    # 是否成功
    success: bool

    # 具体路径
    path: Optional[List[Point]] = None

    next_point: Optional[Point] = None

    model_config = PYDANTIC_DEFAULT_MODEL_CONFIG


class PathFindingAlgorithm(metaclass=ABCMeta):
    """
    寻路算法
    """

    type: PathFindingAlgorithmType

    @abstractmethod
    def find_path(self, input: PathFindingInput, **kwargs) -> PathFindingOutput:
        """
        寻找从start到end的路径
        """
        pass


def default_algorithm_matcher(alg_name: str) -> PathFindingAlgorithmType:
    """
    默认算法匹配器
    根据输入的类型匹配对应的寻路算法
    如果找不到，则返回默认的A*算法
    """
    if alg_name == "default":
        return A_STAR_ALGORITHM

    for _, v in globals().items():
        if isinstance(v, str) and v == alg_name:
            return v
    return A_STAR_ALGORITHM


def get_algorithm(type: PathFindingAlgorithmType) -> Type[PathFindingAlgorithm]:
    """
    根据类型获取对应的寻路算法类
    """
    # TODO：支持热加载模块
    for _, value in globals().items():
        if (
            isclass(value)
            and issubclass(value, PathFindingAlgorithm)
            and getattr(value, "type", None) == type
        ):
            return value
    raise ValueError(f"Unknown pathfinding algorithm type: {type}")


def find_algorithm(resolver: AlgorithmTypeResolver, **kwargs):
    """
    根据解析器和参数获取对应的寻路算法类

    Args:
        resolver: 解析器函数
        kwargs: 解析器需要的参数
    """
    type = resolver(**kwargs)
    return get_algorithm(type)


if __name__ == "__main__":
    pass
