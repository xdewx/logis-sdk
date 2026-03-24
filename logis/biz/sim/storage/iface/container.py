from numbers import Number
from typing import Optional

import simpy

from logis.data_type import QuantifiedValue, Unit


class QuantifiedContainer:
    """
    初衷是统一simpy的Resource、Container、Store等类型并增加单位的概念，但目前还未完全实现

    引入单位的概念，能够简化对simpy的操作，可实现单位换算、检验等功能

    """

    __container__: Optional[simpy.Container] = None

    def __init__(
        self, capacity: QuantifiedValue, env: simpy.Environment, *args, **kwargs
    ):
        self.__quantified_value__ = capacity
        self.__container__ = simpy.Container(env, capacity.quantity)

    @property
    def unit(self) -> Unit:
        return self.__quantified_value__.unit

    @property
    def capacity(self):
        return self.__quantified_value__.quantity

    @property
    def level(self):
        return self.__container__.level

    @property
    def free_capacity(self) -> Number:
        """
        空闲空间
        """
        return self.capacity - self.level

    def get(self, v: QuantifiedValue):
        assert v.unit == self.unit, "unit must be the same"
        return self.__container__.get(v.quantity)

    def put(self, v: QuantifiedValue):
        assert v.unit == self.unit, "unit must be the same"
        return self.__container__.put(v.quantity)
