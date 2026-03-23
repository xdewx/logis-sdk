from abc import ABC, abstractmethod
from typing import Any, Dict, Literal, Optional

from networkx import DiGraph

from logis.data_type import UnitConfig


class IDataReport(ABC):
    pass


class IJsonParser(ABC):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.logic_graph: Optional[DiGraph] = None
        self._produce_recipe_graph: Optional[DiGraph] = None
        self.object_map: Optional[Dict[str, Any]] = None


class IResultGenerator(ABC):
    pass


class IExcelParser(ABC):
    pass


class IOrderManager(ABC):
    pass


class IUnitManager(ABC):

    @abstractmethod
    def find_unit_level(
        self, stock_name: str, unit_name: str
    ) -> Optional[Literal["一级单位", "二级单位", "三级单位"]]:
        pass

    @abstractmethod
    def get_unit_config(self, stock_name: str) -> UnitConfig:
        pass


class IResourceManager(ABC):
    pass


class IStorageManager(ABC):
    pass


class IGraph(ABC):
    pass
