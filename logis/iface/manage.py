from typing import Protocol, runtime_checkable


@runtime_checkable
class IControl(Protocol):
    """
    控制器
    """

    disabled: bool = False
