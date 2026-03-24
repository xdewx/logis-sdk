from .base import *


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
