from typing import Callable, NewType

from logis.alg.pathfinding.model import (
    PathFindingAlgorithmType,
    PathFindingInput,
)
from logis.types import Predicate
from logis.types.point import Point


def test_pathfinding_model():
    assert isinstance(PathFindingAlgorithmType, NewType)
    assert isinstance(Predicate, Callable)

    print("Pathfinding model test passed.")

    input = PathFindingInput(start=Point.of(1, 2), end=Point.of(3, 4))
    input.graph
