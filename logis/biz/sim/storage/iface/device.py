import logging
from abc import abstractmethod
from typing import TYPE_CHECKING, Any, Generator, Tuple, TypeVar

import simpy
from ipa.decorator import deprecated

from logis.biz.sim.const import OperationType
from logis.biz.sim.stock.model import IStock, QuantifiedStock
from logis.data_type.point import Point
from logis.data_type.unitable import unify_quantified_value
from logis.iface import Storable
from logis.math import euclid_distance

from .base import *
from .container import *
from .retrieve import *
from .store import *

if TYPE_CHECKING:
    from logis.biz.sim.agent import IAgent

    from .select import *

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
        self,
        props: Optional[StorageProperties] = None,
        exclusive: bool = True,
        **kwargs
    ):
        """

        Args:
            props: 存储设备的属性
            exclusive: 是否独占，适用于储位、货架、货架组等
        """
        self.props = props
        # 这里以一个不可能达到的数值表示共享
        self.__occupied__ = simpy.Resource(self.env, 1 if exclusive else 10**12)
        if props:
            self.__container__ = QuantifiedContainer(props.capacity, env=self.env)
        else:
            self.__container__ = None
        self.center_point: Optional[Point] = None
        self.current_jobs: int = 0

    def decrease_jobs(self, *args, **kwargs):
        """
        减少作业数
        """
        self.current_jobs -= 1

    def increase_jobs(self, *args, **kwargs):
        """
        增加作业数
        """
        self.current_jobs += 1

    @deprecated("use agent.distance_to instead")
    def distance_to(self, **kwargs) -> float:
        """
        获取到货物源头的距离
        TODO：其实这里按理说应该包括取货距离和送货距离，且放在这里似乎也不太合适
        """
        from logis.biz.sim.agent import IAgent

        # TODO: 考虑过stock不再继承IAgent，所以这里也要考虑改变
        x: IAgent = kwargs.get("agent", None) or kwargs.get("stock", None)
        return euclid_distance(self.center_point, x.resolve_center_point())

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


class ICell(IStorage):
    """
    储位
    """

    @property
    @abstractmethod
    def id(self):
        pass

    @property
    @abstractmethod
    def is_still_universal(self) -> bool:
        pass

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.current_quantity: Optional[simpy.Container] = None
        self.target_quantity: Optional[simpy.Container] = None

    @abstractmethod
    def is_able_to(
        self, operation: OperationType, stock: IStock, strict: bool = False, **kwargs
    ) -> bool:
        """
        判断是否可操作

        Args:
            operation: 操作类型
            stock: 货物
            strict: 是否严格判断，即完全能满足所有货物的需求

        Returns:
            是否可操作
        """
        pass

    @property
    def rack(self) -> Optional["IRack"]:
        raise NotImplementedError("rack not implemented")


CellClass = TypeVar("CellClass", bound=ICell)


class IRack(IStorage):
    """
    货架
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    @abstractmethod
    def cells(self) -> List[ICell]:
        """
        获取本货架下的所有储位
        """
        pass

    @abstractmethod
    def is_able_to(
        self, operation: OperationType, stock: IStock, strict: bool = False, **kwargs
    ) -> bool:
        """
        判断是否能完成某个操作

        Args:
            operation: 操作类型
            stock: 货物
            strict: 是否严格判断，即完全能满足所有货物的需求

        Returns:
            是否能完成操作
        """
        pass

    @property
    def rack_group(self) -> Optional["IRackGroup"]:
        raise NotImplementedError("rack_group not implemented")


RackClass = TypeVar("RackClass", bound=IRack)


class IRackGroup(IStorage):
    """
    货架组
    """

    @property
    @abstractmethod
    def racks(self) -> List[IRack]:
        """
        获取本货架组下的所有货架
        """
        pass

    def handle_operation(
        self,
        operation: Union[str, OperationType],
        stock: IStock,
        strategy: Optional[str] = None,
        agent: Optional["IAgent"] = None,
        force_assign_location: bool = False,
        block: bool = False,
        rack_selection_strategy: Optional["IRackSelectionStrategy"] = None,
        cell_selection_strategy: Optional["ICellSelectionStrategy"] = None,
        **kwargs,
    ) -> Generator[simpy.Event, Any, Tuple[List["IStock"], Optional["IStock"]]]:
        """
        完成指定操作

        Args:
            operation: 操作类型
            stock: 货物
            strategy: 操作策略,此字段已废弃，仅保留兼容性
            agent: 所使用的智能体，可选
            force_assign_location: 是否强制分配位置
            block: 是否等待存取完成
            rack_selection_strategy: 货架选择策略
            cell_selection_strategy: 储位选择策略

        Returns:
            (List["IStock"], Optional["IStock"]): (成功操作的货物列表, 失败的货物)
        """
        raise NotImplementedError("handle_operation not implemented")

    def handle_operation_until(
        self,
        operation: OperationType,
        stock: "IStock",
        try_interval=5,
        max_try: Optional[int] = 1,
        stop_event: Optional[simpy.Event] = None,
        **kwargs,
    ):
        """
        内部调用handle_operation，直到成功或超过最大尝试次数

        Args:
            operation: 操作类型
            stock: 货物
            try_interval: 尝试间隔，单位秒
            max_try: 最大尝试次数,默认1次
            stop_event: 停止事件，触发后停止尝试
            **kwargs: 其他参数，传递给handle_operation

        """
        try_forever = max_try is None
        result = []
        try_count = 0
        while True:
            if stop_event and stop_event.triggered:
                break
            if not try_forever and try_count >= max_try:
                break
            stocks, stock_left = yield from self.handle_operation(
                operation, stock, **kwargs
            )
            result.extend(stocks)
            stock = stock_left
            if not try_forever or not stock_left:
                break
            try_count += 1
            if try_forever or try_count < max_try:
                yield self.env.timeout(try_interval)
        return result, stock


RackGroupClass = TypeVar("RackGroupClass", bound=IRackGroup)
