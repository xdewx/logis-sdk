from typing import Protocol, runtime_checkable

from logis.biz.sim.stock.model import QuantifiedStock

from ..model import *


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
