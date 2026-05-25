import sys
from decimal import Decimal
from fractions import Fraction
from numbers import Number
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    Generic,
    List,
    NewType,
    Optional,
    Self,
    Tuple,
    TypeVar,
    Union,
)

import humps
import pint
from pydantic import BaseModel, ConfigDict, Field
from typing_extensions import TypeAlias

StringNumber: TypeAlias = str

BaseNumberType: TypeAlias = Union[int, float]
NumberType: TypeAlias = Union[Decimal, int, float, Fraction]

ComponentIntId: TypeAlias = int

ComponentStrId: TypeAlias = str

ComponentId: TypeAlias = Union[ComponentIntId, ComponentStrId]

if sys.version_info >= (3, 9):
    TmpId: TypeAlias = Union[int, str]
else:
    TmpId = Union[int, str]


T = TypeVar("T")
Predicate: TypeAlias = Callable[[T], bool]

Unit: TypeAlias = Union[pint.Unit, str]

# 倍率计算器，输入源单位、目标单位，输出倍率
RatioComputer: TypeAlias = Callable[[Unit, Unit], Decimal]

EventType = NewType("EventType", str)
TaskType = NewType("TaskType", str)

TuplePoint: TypeAlias = Tuple[Optional[Number], Optional[Number], Optional[Number]]

if TYPE_CHECKING:
    from .unitable import Length

# 这里不要随便改，如果不满足自己的需求，可以新建配置
DEFAULT_PYDANTIC_MODEL_CONFIG = ConfigDict(
    strict=False,
    arbitrary_types_allowed=True,
    extra="ignore",
    validate_by_alias=True,
    validate_by_name=True,
    coerce_numbers_to_str=True,
    alias_generator=humps.camelize,
    populate_by_name=True,
)
class CallableInput(BaseModel):
    args: Tuple = Field(default_factory=tuple)
    kwargs: Dict[str, Any] = Field(default_factory=dict)

    @staticmethod
    def of(*args, **kwargs):
        return CallableInput(args=args, kwargs=kwargs)

    def get(self, key: str, default=None):
        """
        从kwargs中获取参数
        """
        return self.kwargs.get(key, default)


class InvokeResult:

    def __init__(self, **kwargs):
        super().__init__()
        self.is_generator = False
        self.return_value: Any = None
        self.yield_values: Any = []

    @staticmethod
    def returns(value: Any):
        self = InvokeResult()
        self.return_value = value
        return self


class Data(BaseModel, Generic[T]):
    model_config = DEFAULT_PYDANTIC_MODEL_CONFIG
    type: str
    value: T
    tags: Optional[List[str]] = None
    description: Optional[str] = None


from abc import ABC, ABCMeta, abstractmethod
from enum import EnumMeta


class ABCEnumMeta(EnumMeta, ABCMeta):
    """
    适用于enum类继承但是提示metaclass冲突的情况
    1. 置顶metaclass为本类即可
    """

    pass


class Interface(ABC):
    """
    为了避免多继承的参数传递问题，这里兜底处理所有多余参数

    使用时全部继承本接口即可
    """

    def __init__(self, *args, **kwargs) -> None:
        super().__init__()


class Locatable(Interface):
    """
    可定位的，带有位置信息
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

    @abstractmethod
    def distance_to(self, target: Self, **kwargs) -> "Length":
        """
        到目标的距离

        Args:
            target: 目标

        Returns:
            距离
        """
        pass
