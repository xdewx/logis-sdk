from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Dict, Literal, Optional

from networkx import DiGraph

from logis.data_type import UnitConfig

from .blueprint import IBlueprint

if TYPE_CHECKING:
    from logis.biz.sim.ctx import Context


class IExpose(ABC):
    """
    用于通过SDK向外暴露参数
    """

    def __init__(self, ctx: "Context", **kwargs) -> None:
        super().__init__()
        self.ctx = ctx


class IDataReport(ABC):

    def __init__(self, **kwargs) -> None:
        super().__init__()


class IJsonParser(ABC):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.logic_graph: Optional[DiGraph] = None
        self._produce_recipe_graph: Optional[DiGraph] = None
        # TODO：考虑使用id_instance_map来代替
        self.object_map: Optional[Dict[str, IBlueprint]] = None

    @property
    def id_instance_map(self) -> Dict[str, "IBlueprint"]:
        assert self.object_map, "请先解析JSON文件"
        return self.object_map


class IResultGenerator(ABC):

    def __init__(self, **kwargs) -> None:
        super().__init__()


class IExcelParser(ABC):

    def __init__(self, **kwargs) -> None:
        super().__init__()


class IOrderManager(ABC):

    def __init__(self, **kwargs) -> None:
        super().__init__()


class IUnitManager(ABC):

    def __init__(self, **kwargs) -> None:
        super().__init__()

    @abstractmethod
    def find_unit_level(
        self, stock_name: str, unit_name: str
    ) -> Optional[Literal["一级单位", "二级单位", "三级单位"]]:
        pass

    @abstractmethod
    def get_unit_config(self, stock_name: str) -> UnitConfig:
        pass


class IResourceManager(ABC):

    def __init__(self, **kwargs) -> None:
        super().__init__()


class IStorageManager(ABC):

    def __init__(self, **kwargs) -> None:
        super().__init__()
