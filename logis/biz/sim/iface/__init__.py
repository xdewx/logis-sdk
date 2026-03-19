__doc__ = """
仿真模块接口
"""

from typing import Protocol

from .component import *
from .order import *
from .picking import *
from .wave import *


class IControl(Protocol):
    """
    控制器，用于控制仿真的进行
    """

    disabled: bool = False
