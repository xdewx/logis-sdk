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
    Type,
    Union,
)

from logis.data_type import Point

Path = List[Point]


PathFindingAlgorithmType = NewType("PathFindingAlgorithmType", str)

AlgorithmTypeResolver = Callable[[Any], PathFindingAlgorithmType]

# TODO: 完善名字、补充类型
A_STAR_ALGORITHM = PathFindingAlgorithmType("a_star")
DIJKSTRA_ALGORITHM = PathFindingAlgorithmType("dijkstra")

if TYPE_CHECKING:
    from .model import (
        PathFindingInput,
        PathFindingOutput,
    )


class PathFindingAlgorithm(metaclass=ABCMeta):
    """
    寻路算法
    """

    type: Union[PathFindingAlgorithmType, str]

    @abstractmethod
    def find_path(self, input: "PathFindingInput", **kwargs) -> "PathFindingOutput":
        """
        寻找从start到end的路径
        """
        pass


def default_algorithm_matcher(alg_name: str, **space) -> PathFindingAlgorithmType:
    """
    默认算法匹配器
    根据输入的类型匹配对应的寻路算法
    如果找不到，则返回默认的A*算法
    """
    if alg_name == "default":
        return A_STAR_ALGORITHM

    for _, v in (space or globals()).items():
        if isinstance(v, str) and v == alg_name:
            return v
    return A_STAR_ALGORITHM


def get_algorithm(
    type: PathFindingAlgorithmType, **space
) -> Type[PathFindingAlgorithm]:
    """
    根据类型获取对应的寻路算法类
    """
    # TODO：支持热加载模块
    for _, value in (space or globals()).items():
        if (
            isclass(value)
            and issubclass(value, PathFindingAlgorithm)
            and getattr(value, "type", None) == type
        ):
            return value
    raise ValueError(f"Unknown pathfinding algorithm type: {type}")


def find_algorithm(
    resolver: AlgorithmTypeResolver, space: Optional[Dict] = None, **kwargs
) -> Type[PathFindingAlgorithm]:
    """
    根据解析器和参数获取对应的寻路算法类

    Args:
        resolver: 解析器函数
        kwargs: 解析器需要的参数
    """
    type = resolver(**kwargs)
    return get_algorithm(type, **space)


def track_path(
    tree: Dict[Point, List[Point]],
    source: Point,
    target: Optional[Point] = None,
    limit=None,
) -> List[Path]:
    """
    正向生成路线，找到到终点的所有路线
    """

    paths = []

    def dfs(path: Path, root: Point):
        if (limit is not None and len(path) == limit) or (root is None):
            paths.append(path)
            return
        path.append(root)
        if root == target:
            paths.append(path)
            return
        children = tree.get(root, [])
        if not children:
            dfs(path.copy(), None)
            return
        for child in children:
            dfs(path.copy(), child)

    dfs([], source)
    return paths
