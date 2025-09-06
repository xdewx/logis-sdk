from decimal import Decimal
from fractions import Fraction
from numbers import Number
from typing import Callable, NewType, Optional, Tuple, TypeAlias, TypeVar, Union

from pydantic import ConfigDict

StringNumber: TypeAlias = str

BaseNumberType: TypeAlias = Union[int, float]
NumberType: TypeAlias = Union[Decimal, int, float, Fraction, Number]

ComponentIntId: TypeAlias = int

ComponentStrId: TypeAlias = str

ComponentId: TypeAlias = Union[ComponentIntId, ComponentStrId]

TmpId: TypeAlias = Union[int, str]


T = TypeVar("T")
Predicate: TypeAlias = Callable[[T], bool]

Unit = NewType("Unit", str)

# 倍率计算器，输入源单位、目标单位，输出倍率
RatioComputer: TypeAlias = Callable[[Unit, Unit], Decimal]

EventType = NewType("EventType", str)
TaskType = NewType("TaskType", str)

TuplePoint: TypeAlias = Tuple[Optional[Number], Optional[Number], Optional[Number]]

# 这里不要随便改，如果不满足自己的需求，可以新建配置
DEFAULT_PYDANTIC_MODEL_CONFIG = ConfigDict(
    arbitrary_types_allowed=True,
    extra="ignore",
    validate_by_alias=True,
    validate_by_name=True,
)

from .point import *

__doc__ = """
类型模块
"""
