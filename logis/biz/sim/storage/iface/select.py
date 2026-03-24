from abc import ABC, abstractmethod
from typing import List

from logis.biz.sim.const import OperationType
from logis.biz.sim.stock.model import IStock

from .device import CellClass, RackClass


class IRackSelectionStrategy(ABC):
    """
    货架选择策略，从若干货架中筛选出符合操作需求的货架
    """

    @abstractmethod
    def get_all_racks(self, *args, **kwargs) -> List[RackClass]:
        """
        获取所有可操作的货架
        """
        pass

    @abstractmethod
    def select_racks(
        self, operation: OperationType, stocks: List[IStock], **kwargs
    ) -> List[RackClass]:
        """
        从所有可操作的货架中筛选出符合操作需求的货架
        """
        pass


class ICellSelectionStrategy(ABC):
    """
    储位选择策略，从若干储位中筛选出符合操作需求的储位
    """

    @abstractmethod
    def get_all_cells(self, *args, **kwargs) -> List[CellClass]:
        """
        获取所有可操作的储位
        """
        pass

    @abstractmethod
    def select_cells(
        self, operation: OperationType, stocks: List[IStock], **kwargs
    ) -> List[CellClass]:
        """
        从所有可操作的储位中筛选出符合操作需求的储位
        """
        pass
