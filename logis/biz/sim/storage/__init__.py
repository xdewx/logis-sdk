import logging
from abc import abstractmethod
from numbers import Number
from typing import Protocol, runtime_checkable

import simpy

from logis.biz.sim.const import OperationType
from logis.biz.sim.stock.model import QuantifiedStock
from logis.data_type.unitable import QuantifiedValue, Unit, unify_quantified_value
from logis.iface import Storable

from .model import *


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


@runtime_checkable
class StorageStrategy(Protocol):
    """
    存取策略
    """

    def find_location(
        self, storage: StorageProperties, stocks: List[QuantifiedStock], *args, **kwargs
    ) -> List[CellProperties]:
        """
        寻找储位位置，存储获取或者取出货物
        """
        raise NotImplementedError()


class StoreStrategy(StorageStrategy):
    """
    存储策略
    """

    def find_location(
        self, storage: StorageProperties, stocks: List[QuantifiedStock], *args, **kwargs
    ) -> List[CellProperties]:
        result = []
        type_cells_map = storage.group_cell_by_stock_type()
        for stock in stocks:
            # 过滤出可以容纳此货物的所有储位
            candidates = type_cells_map.get(stock.unique_id, []) + type_cells_map.get(
                "*", []
            )
            for candidate in candidates:
                if candidate.can_store(stock):
                    result.append(candidate)
                    break
        return result


class RetrieveStrategy(StorageStrategy):
    """
    取回策略
    """

    def find_location(
        self, storage: StorageProperties, stocks: List[QuantifiedStock], *args, **kwargs
    ) -> List[CellProperties]:
        result = []
        type_cells_map = storage.group_cell_by_stock_type()
        for stock in stocks:
            # 过滤出可以容纳此货物的所有储位
            candidates = type_cells_map.get(stock.unique_id, []) + type_cells_map.get(
                "*", []
            )
            for candidate in candidates:
                if candidate.can_retrieve(stock):
                    result.append(candidate)
        return result


class IStorage(Storable):
    """
    存储设备
    """

    store_strategy: Optional[StoreStrategy] = StoreStrategy()
    retrieve_strategy: Optional[RetrieveStrategy] = RetrieveStrategy()

    props: Optional[StorageProperties] = None

    __resource__: Optional[simpy.Resource] = None

    # 表明当前存储空间是否被占用
    __occupied__: Optional[simpy.Resource] = None

    __container__: Optional[QuantifiedContainer] = None

    log: logging.Logger

    @property
    @abstractmethod
    def env(self) -> simpy.Environment:
        pass

    def __init__(
        self, props: StorageProperties, exclusive: bool = True, *args, **kwargs
    ):
        """
        Args:
            exclusive: 是否独占，适用于储位、货架、货架组等
        """
        self.props = props
        # 这里以一个不可能达到的数值表示共享
        self.__occupied__ = simpy.Resource(self.env, 1 if exclusive else 10**12)
        p = self.props
        self.__container__ = QuantifiedContainer(p.capacity, env=self.env)

    @property
    def level(self):
        return self.__container__.level

    @property
    def capacity(self):
        return self.__container__.capacity

    @property
    def unit(self):
        return self.__container__.unit

    @property
    def free_capacity(self):
        return self.__container__.free_capacity

    def store(self, v: QuantifiedStock, *args, **kwargs):
        """
        存储
        """
        log = self.log
        v = unify_quantified_value(v, self.unit)
        cells = self.store_strategy.find_location(self.props, [v])
        with self.__occupied__.request() as req:
            # yield req
            if self.free_capacity < v.quantity:
                log.warning("%s < %s, skip store", self.free_capacity, v.quantity)
                yield self.env.timeout(0)
                return
            for cell in cells:
                cell.store(v)
            yield self.__container__.put(v)
            t = self.props.store_speed_time
            yield self.env.timeout(0 if not t else t.value)

    def retrieve(self, v: QuantifiedStock, *args, **kwargs):
        """
        取回
        """
        log = self.log
        v = unify_quantified_value(v, self.unit)
        cells = self.retrieve_strategy.find_location(self.props, [v])
        with self.__occupied__.request() as req:
            yield req
            if v.quantity > self.level:
                log.warning("%s < %s, skip retrieve", self.level, v.quantity)
                yield self.env.timeout(0)
                return
            for cell in cells:
                cell.retrieve(v)
            yield self.__container__.get(v)
            t = self.props.retrieve_speed_time or self.props.store_speed_time
            yield self.env.timeout(0 if not t else t.value)
