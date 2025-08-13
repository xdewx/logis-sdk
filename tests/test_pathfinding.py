from typing import Callable, NewType

from logis.alg.pathfinding.model import (
    PathFindingAlgorithmType,
    PathFindingInput,
    Predicate,
)


def test_pathfinding_model():
    assert isinstance(PathFindingAlgorithmType, NewType)
    assert isinstance(Predicate, Callable)

    print("Pathfinding model test passed.")

    input = PathFindingInput()
