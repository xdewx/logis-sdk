from abc import ABCMeta, abstractmethod
from inspect import isclass
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    List,
    NewType,
    Optional,
    Protocol,
    Tuple,
    Type,
    TypeAlias,
    TypeVar,
)

from pydantic import BaseModel, Field

from logis.conf import PYDANTIC_DEFAULT_MODEL_CONFIG
from logis.types import Point

if TYPE_CHECKING:
    pass

PathFindingAlgorithmType = NewType("PathFindingAlgorithmType", str)

AlgorithmTypeResolver: TypeAlias = Callable[[Any], PathFindingAlgorithmType]

# TODO: 完善名字、补充类型
A_STAR_ALGORITHM = PathFindingAlgorithmType("a_star")
DIJKSTRA_ALGORITHM = PathFindingAlgorithmType("dijkstra")


class PathFindingInput(BaseModel):
    alg: str | None = None

    # 起点
    start: Point
    # 终点
    end: Point
    # 点到点的距离矩阵
    distance_matrix: Dict[Point, List[Tuple[Point, float]]] = Field(
        default_factory=dict
    )
    # 排除的点
    excluded_vertices: List[Point] = []
    # 启发式距离计算方法
    heuristic_func: Callable[[Point, Point], float] = None

    model_config = PYDANTIC_DEFAULT_MODEL_CONFIG


class PathFindingOutput(BaseModel):
    # 是否成功
    success: bool
    # 具体路径
    path: Optional[List[Point]] = None

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

def default_algorithm_matcher(method: str) -> PathFindingAlgorithmType:
    """
    默认算法匹配器
    根据输入的类型匹配对应的寻路算法
    如果找不到，则返回默认的A*算法
    """
    if method == "default":
        return A_STAR_ALGORITHM

    for _, v in globals().items():
        if v == method and isinstance(v, str):
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
