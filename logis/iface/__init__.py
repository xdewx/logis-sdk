from abc import ABC, ABCMeta
from collections import defaultdict
from typing import Dict, Generic, Protocol, TypeVar, runtime_checkable

from logis.data_type import NumberType, NumberUnit, SpatialProps
from logis.util.num_util import get_numeric_value


class Shape(metaclass=ABCMeta):
    """
    形状，例如路径、节点等
    """

    @property
    def rotation_value(self):
        v = get_numeric_value(self.props.rotation) if self.props else None
        return v or 0

    def __init__(self, **kwargs):
        self.props: SpatialProps | None = None


@runtime_checkable
class Producer(Protocol):
    """
    生产者
    """

    def produce(self, *args, **kwargs):
        pass


@runtime_checkable
class Consumer(Protocol):
    """
    消费者
    """

    def consume(self, *args, **kwargs):
        pass


class StoreResult(metaclass=ABCMeta):
    """
    存储结果
    """

    pass


class RetrieveResult(metaclass=ABCMeta):
    """
    检索结果
    """

    pass


class StoreStrategy(metaclass=ABCMeta):
    """
    存储策略
    """


@runtime_checkable
class Storable(Protocol):
    # class Storable(metaclass=ABCMeta):
    """
    可存储的

    使用鸭子类型实现，相比ABC更灵活
    """

    def pre_store(self, *args, **kwargs):
        pass

    def pre_retrieve(self, *args, **kwargs):
        pass

    def store(self, *args, **kwargs) -> StoreResult:
        pass

    def retrieve(self, *args, **kwargs) -> RetrieveResult:
        pass


class QuantifiedValueContainer(Storable):

    def __init__(self):
        self.__container__: Dict[str, Dict[str, NumberType]] = defaultdict(
            defaultdict(0)
        )

    def store(self, v: "NumberUnit"):
        self.__container__[v.kind][v.unit] += v.quantity

    def retrieve(self, v: "NumberUnit"):
        self.__container__[v.kind][v.unit] -= v.quantity


T = TypeVar("T")


@runtime_checkable
class IQueue(Protocol[T]):
    """
    队列接口
    """

    def __init__(self, maxsize: int = 0):
        super().__init__(maxsize)

    def put(self, item: T, *args, **kwargs):
        pass

    def put_nowait(self, item: T):
        pass

    def get(self, *args, **kwargs) -> T:
        pass

    def get_nowait(self) -> T:
        pass

    def qsize(self) -> int:
        pass

    def empty(self) -> bool:
        pass

    def full(self) -> bool:
        pass


QueueType = TypeVar("QueueType", bound=IQueue[T])
