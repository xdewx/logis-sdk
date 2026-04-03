from decimal import ROUND_HALF_UP, Decimal
from itertools import count
from numbers import Number
from typing import Dict, Generic, Optional, Tuple, TypeVar

from logis.data_type import Number, TuplePoint

from ._math import compute

Num = TypeVar("T", bound=Number)


def round_if_not_none(
    value: Optional[Num], ndigits: Optional[int] = None, rounding=ROUND_HALF_UP
) -> Optional[Num]:
    """
    当value和ndigits都不为None时，进行四舍五入，否则返回原数值。

    :param value: 要四舍五入的值
    :type value: Optional[T]
    :param ndigits: 四舍五入的小数位数，**与原round的行为不同的是，这里为None时返回原数值**
    :type ndigits: Optional[int]
    :return: 四舍五入后的值
    :rtype: T | None
    """
    if value is not None and ndigits is not None:
        # 这里如果不用str转换，float的精度问题仍然会导致结果不正确，例如1216.745、1216.74512等
        v = Decimal(str(value)).quantize(
            Decimal("0." + "0" * ndigits), rounding=rounding
        )
        # if int(value) == 976:
        #     print(value, v, float(v))
        if type(value) is type(v):
            return v
        return type(value)(v)
    return value


def cast_if_not_none(value: Optional[Num], type_: type[Num]) -> Optional[Num]:
    """
    当value不为None时，转换为指定类型，否则返回None。

    :param value: 要转换的值
    :type value: Optional[T]
    :param type_: 目标类型
    :type type_: type[T]
    :return: 转换后的值
    :rtype: T | None
    """
    if value is not None:
        return type_(value)
    return None


class GenericPoint(Generic[Num]):
    __global_precision__: Optional[int] = None

    @property
    def precision(self) -> Optional[int]:
        """
        优先读取__precision_，否则读取__global_precision__
        """
        return self.__precision__ or self.__class__.__global_precision__

    @precision.setter
    def precision(self, value: Optional[int]):
        self.__precision__ = value

    @classmethod
    def model_validate(cls, v: Dict[str, Num]):
        if v is None:
            return None
        if isinstance(v, dict):
            return cls(**v)
        raise ValueError("only dict type is supported")

    def __init__(
        self,
        x: Optional[Num] = None,
        y: Optional[Num] = None,
        z: Optional[Num] = None,
        *args,
        precision: Optional[int] = None,
        **kwargs,
    ):
        """
        Args:
            x (T | None, optional): X coordinate. Defaults to None.
            y (T | None, optional): Y coordinate. Defaults to None.
            z (T | None, optional): Z coordinate. Defaults to None.
            precision (int | None, optional): Precision. Defaults to None.
        """
        self.precision = precision
        if (p := self.precision) is not None:
            assert p > 0, "precision must be greater than 0."
            x = round_if_not_none(x, p)
            y = round_if_not_none(y, p)
            z = round_if_not_none(z, p)
        self.x, self.y, self.z = x, y, z

    @classmethod
    def from_tuple(
        cls, tp: Tuple[Num], precision: Optional[int] = None, **kwargs
    ) -> "GenericPoint[Num]":
        return cls(*tp, precision=precision, **kwargs)

    def __add__(self, other: "GenericPoint[Num]") -> "GenericPoint[Num]":
        assert self.precision == other.precision, "Precision must be the same."
        x = compute("add", self.x, other.x)
        y = compute("add", self.y, other.y)
        z = compute("add", self.z, other.z)
        return self.__class__(x, y, z, precision=self.precision)

    def __sub__(self, other: "GenericPoint[Num]") -> "GenericPoint[Num]":
        assert self.precision == other.precision, "Precision must be the same."
        x = compute("subtract", self.x, other.x)
        y = compute("subtract", self.y, other.y)
        z = compute("subtract", self.z, other.z)
        return self.__class__(x, y, z, precision=self.precision)

    def __mul__(self, other: Number) -> "GenericPoint[Num]":
        assert other is not None, "Multiplier must not be None."
        x = compute("multiply", self.x, other) if self.x is not None else None
        y = compute("multiply", self.y, other) if self.y is not None else None
        z = compute("multiply", self.z, other) if self.z is not None else None
        return self.__class__(x, y, z, precision=self.precision)

    def __truediv__(self, other: Number) -> "GenericPoint[Num]":
        assert other is not None, "Divisor must not be None."
        x = compute("divide", self.x, other) if self.x is not None else None
        y = compute("divide", self.y, other) if self.y is not None else None
        z = compute("divide", self.z, other) if self.z is not None else None
        return self.__class__(x, y, z, precision=self.precision)

    def __eq__(self, value):
        if not isinstance(value, self.__class__):
            return False
        dv = 1 / (10**self.precision) if self.precision else None

        def is_acceptable(a: Optional[Number], b: Optional[Number]) -> bool:
            if dv is None:
                return a == b
            if a is None and b is None:
                return True
            if a is None or b is None:
                return False
            return abs(a - b) < dv

        return (
            is_acceptable(self.x, value.x)
            and is_acceptable(self.y, value.y)
            and is_acceptable(self.z, value.z)
            and self.precision == value.precision
            and self.unit == value.unit
        )


class Point(GenericPoint[float]):
    """
    此类不通用，历史遗留，不建议使用，如有需要建议使用GenericPoint
    支持x,y,z三维坐标点，也可当作二维坐标使用
    TODO: 处理单位
    """

    __counter = count(0, step=1)
    __global_precision__ = 3

    @classmethod
    def try_parse(cls, dc: dict, **kwargs) -> "Point":
        """
        尝试读取X、Y、Z坐标，返回一个Point对象
        """
        if not isinstance(dc, dict):
            raise ValueError("Expected a dictionary for Point parsing.")
        xyz = [dc.get(k, None) for k in ("X", "Y", "Z")]
        return Point(xyz, **kwargs)

    @classmethod
    def from_tuple(cls, args: Tuple[Number], **kwargs):
        """
        从元组创建点
        """
        return cls(args, **kwargs)

    @classmethod
    def of(
        cls,
        x: Optional[Number] = None,
        y: Optional[Number] = None,
        z: Optional[Number] = None,
        **kwargs,
    ) -> "Point":
        p = Point(x, y, z, **kwargs)
        return p

    def __init__(self, *args, precision: Optional[int] = None, **kwargs):
        """
        支持[x,y]、x,y、[x,y,z]、x,y,z传参赋值
        默认x=y=z=0

        TODO: 不应该自动转float、不应该自动保留两位小数
        """
        self._id = next(self.__counter)
        self.unit: Optional[str] = kwargs.get("unit", None)

        x: Optional[Number] = kwargs.get("x", None)
        y: Optional[Number] = kwargs.get("y", None)
        z: Optional[Number] = kwargs.get("z", None)
        if len(args) == 1:
            assert isinstance(
                args[0], (list, tuple)
            ), "single argument must be a list or tuple."
            x = cast_if_not_none(args[0][0], float)
            y = cast_if_not_none(args[0][1], float)
            if len(args[0]) > 2 and (z := args[0][2]) is not None:
                z = cast_if_not_none(z, float)

        elif len(args) >= 2:
            x = cast_if_not_none(args[0], float)
            y = cast_if_not_none(args[1], float)
            if len(args) > 2 and (z := args[2]) is not None:
                z = cast_if_not_none(z, float)

        # 调试过程中发现z有时候是None有时候是0，因此这里统一给了默认值
        # 实际上应该外层规范
        x = x if x is not None else 0
        y = y if y is not None else 0
        z = z if z is not None else 0

        kwargs.update(x=x, y=y, z=z)

        super().__init__(precision=precision, **kwargs)

    def __repr__(self):
        return f"Point({self.x}, {self.y}, {self.z})"

    def __hash__(self):

        def s(v: Optional[Number]):
            if not self.precision:
                return v
            if v is None:
                return v
            return v
            # return str(Decimal(v).quantize(Decimal(f"0.{'0'*self.precision}")))

        # if self._id is not None:
        #     return hash((self.__class__.__name__, self._id))
        return hash((s(self.x), s(self.y), s(self.z), self.precision, self.unit))

    def __lt__(self, other):
        """
        FIXME: 考虑z
        """
        if isinstance(other, Point):
            # TODO: 只要任何一个大于就行？
            return (self.x, self.y) < (other.x, other.y)
        return NotImplemented

    def __sub__(self, other: "Point"):
        def sub(a: Number, b: Number):
            if a is None and b is None:
                return None
            a = a or 0
            b = b or 0
            return a - b

        assert self.unit == other.unit, "unit must be same"
        return Point.of(
            x=sub(self.x, other.x),
            y=sub(self.y, other.y),
            z=sub(self.z, other.z),
            unit=self.unit,
        )

    def to_tuple(self) -> TuplePoint:
        return (
            self.x,
            self.y,
            self.z,
        )

    def __str__(self):
        return f"Point(id={self._id},x={self.x},y={self.y},z={self.z})"


if __name__ == "__main__":
    pass
