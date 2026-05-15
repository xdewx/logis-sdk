from typing import Protocol, runtime_checkable


@runtime_checkable
class IControl(Protocol):
    """
    控制器
    """

    disabled: bool = False

    def __init__(self, **kwargs) -> None:
        super().__init__()
