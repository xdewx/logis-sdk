from typing import TYPE_CHECKING

from .base import (
    PathFindingAlgorithm,
)
from .model import PathFindingInput, PathFindingOutput

if TYPE_CHECKING:
    pass


class CbsPathFinding(PathFindingAlgorithm):
    """
    CBS寻路算法实现
    """

    type = "cbs"

    def find_path(self, input: PathFindingInput, **kwargs) -> PathFindingOutput:
        """
        使用CBS算法寻找从start到end的路径
        """
        raise NotImplementedError("CBS算法未实现")
        from mapf.centralized.cbs import CBS, Environment
        from mapf.model import AgentInfo, MapfInput, MapfOutput, MapInfo

        env = Environment.from_mapf_input()
        MapfInput(
            map=MapInfo(
                dimensions=input.graph,
                obstacles=list(map(lambda p: p.to_tuple(), input.excluded_vertices)),
            ),
            agents=[
                AgentInfo(
                    name=0,
                    start=input.start.to_tuple(),
                    goal=input.end.to_tuple(),
                )
            ],
        )

        cbs = CBS(env)
        out = cbs.search()
