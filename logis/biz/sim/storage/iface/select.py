from abc import abstractmethod
from typing import TYPE_CHECKING, Generic, List, Optional, TypeVar, Union

from logis.biz.sim.const import (
    LocationSelectionStrategy,
    OperationType,
    StorageSelectionStrategy,
)
from logis.biz.sim.iface import IExpose, Locatable
from logis.biz.sim.stock.model import IStock

from .device import CellClass, IRack, RackClass, RackGroupClass

L = TypeVar("L", bound=Locatable)

if TYPE_CHECKING:
    from logis.biz.sim.agent import IAgent

class ILocationSelectionStrategy(IExpose, Generic[L]):
    """
    位置选择策略
    """

    def __init__(self, candidates: Optional[List[L]] = None, **kwargs):
        """
        Args:
            candidates (Optional[List[L]], optional): 可选位置列表. Defaults to None.
        """
        super().__init__(**kwargs)
        self.candidates = candidates

    @abstractmethod
    def select_location(
        self,
        operation: OperationType,
        stock: IStock,
        candidates: Optional[List[L]] = None,
        **kwargs,
    ) -> Union["L", List["L"], None]:
        """
        选择位置

        Args:
            operation (OperationType): 操作类型
            stock (IStock): 货物
            candidates (Optional[List[L]], optional): 可选位置. 如果不填则初始化时应传入

        Returns:
            选择的位置
        """


class DefaultLocationSelectionStrategy(ILocationSelectionStrategy[L]):
    def __init__(self, candidates: List[L] | None = None, **kwargs):
        super().__init__(candidates=candidates, **kwargs)

    def select_location(
        self,
        operation: OperationType,
        stock: IStock,
        candidates: List[L] | None = None,
        strategy: Optional[LocationSelectionStrategy] = None,
        **kwargs,
    ) -> L | List[L] | None:
        if LocationSelectionStrategy.DistanceAscend.matches(strategy):
            agent: "IAgent" = kwargs.get("agent") or kwargs.get("stock")
            return sorted(
                candidates,
                key=lambda x: x.distance_to(target=agent, stock=stock, **kwargs),
            )
        if LocationSelectionStrategy.BusyLevelAscend.matches(strategy):
            return sorted(
                candidates,
                key=lambda x: x.current_jobs,
            )
        elif strategy:
            raise NotImplementedError(f"暂不支持 {strategy} 策略")
        return candidates


class IRackSelectionStrategy(ILocationSelectionStrategy[IRack]):
    """
    货架选择策略，从若干货架中筛选出符合操作需求的货架
    """

    def __init__(
        self, rack_group: Union[RackGroupClass, None] = None, **kwargs
    ) -> None:
        """
        初始化货架选择策略

        Args:
            rack_group: 货架组，如果此策略仅针对特定货架组则建议传，否则忽略即可
        """
        super().__init__(**kwargs)
        self.rack_group = rack_group

    def select_location(
        self,
        operation: OperationType,
        stock: IStock,
        candidates: RackGroupClass | None = None,
        **kwargs,
    ) -> List[IRack]:
        return self.select_racks(
            operation=operation, stock=stock, rack_group=candidates, **kwargs
        )

    @abstractmethod
    def select_racks(
        self,
        operation: OperationType,
        stock: IStock,
        rack_group: Optional[RackGroupClass] = None,
        **kwargs,
    ) -> List[IRack]:
        """
        从所有可操作的货架中筛选出符合操作需求的货架

        Args:
            operation: 操作类型
            stocks: 货物列表
            rack_group: 货架组，如果不传则使用初始化时传的货架组

        Returns:
            符合操作需求的货架列表
        """
        rack_group = rack_group or self.rack_group
        assert rack_group is not None, "未传入货架组，无法选择货架"
        result: List[RackClass] = []
        for rack in rack_group.racks:
            if not rack.is_able_to(operation, stock):
                continue
            result.append(rack)
        return result


class DefaultRackSelectionStrategy(IRackSelectionStrategy):
    """
    默认货架选择策略
    """

    def select_racks(
        self,
        operation: OperationType,
        stock: IStock,
        rack_group: Optional[RackGroupClass] = None,
        strategy: Optional[StorageSelectionStrategy] = None,
        **kwargs,
    ):
        """
        默认货架选择策略

        Args:
            operation: 操作类型
            stock: 货物
            rack_group: 货架组，如果不传则使用初始化时传的货架组
            strategy: 此方式实际上不是规范的策略模式，仅仅是为了少写代码

        Returns:
            符合操作需求的货架列表
        """
        racks = super().select_racks(
            operation=operation, stock=stock, rack_group=rack_group, **kwargs
        )
        if not racks:
            return racks
        if StorageSelectionStrategy.BusyLevelAscend.matches(strategy):
            racks.sort(key=lambda x: x.current_jobs)
        elif StorageSelectionStrategy.DistanceAscend.matches(strategy):
            racks.sort(key=lambda x: x.distance_to(stock=stock, **kwargs))
        return racks


class ICellSelectionStrategy(IExpose):
    """
    储位选择策略，从若干储位中筛选出符合操作需求的储位
    """

    def __init__(self, rack: Optional[RackClass] = None, **kwargs) -> None:
        """
        初始化储位选择策略

        Args:
            rack: 货架，如果此策略仅针对特定货架则建议传，否则忽略即可
        """
        super().__init__(**kwargs)
        self.rack = rack

    @abstractmethod
    def select_cells(
        self,
        operation: OperationType,
        stock: IStock,
        rack: Optional[RackClass] = None,
        **kwargs,
    ) -> List[CellClass]:
        """
        从所有可操作的储位中筛选出符合操作需求的储位

        Args:
            operation: 操作类型
            stocks: 货物列表
            rack: 货架，如果不传则使用初始化时传的货架

        Returns:
            符合操作需求的储位列表
        """
        pass


class DefaultCellSelectionStrategy(ICellSelectionStrategy):
    """
    默认储位选择策略
    """

    def select_cells(
        self,
        operation: OperationType,
        stock: IStock,
        rack: Optional[RackClass] = None,
        strategy: Optional[StorageSelectionStrategy] = None,
        **kwargs,
    ) -> List[CellClass]:
        rack = rack or self.rack
        assert rack is not None, "未传入货架，无法选择储位"
        cells = [
            cell for cell in rack.cells if cell.is_able_to(operation, stock, **kwargs)
        ]
        if not cells:
            return cells
        if StorageSelectionStrategy.NumberAscend.matches(strategy):
            if OperationType.Store.matches(operation):
                cells.sort(
                    key=lambda x: (
                        1 if x.is_still_universal else 0,
                        -x.target_quantity.capacity + x.target_quantity.level,
                        x.id,
                    )
                )
            else:
                cells.sort(key=lambda x: (-x.target_quantity.level, x.id))
        elif StorageSelectionStrategy.DistanceAscend.matches(strategy):
            if OperationType.Store.matches(operation):
                cells.sort(
                    key=lambda x: (
                        0 if x.is_still_universal else 1,
                        x.target_quantity.capacity - x.target_quantity.level,
                        x.id,
                    ),
                    reverse=True,
                )
            else:
                cells.sort(
                    key=lambda x: (
                        x.target_quantity.level,
                        x.id,
                    ),
                    reverse=True,
                )
        else:
            raise NotImplementedError(f"尚未支持的储位选择策略:{strategy}")
        return cells
