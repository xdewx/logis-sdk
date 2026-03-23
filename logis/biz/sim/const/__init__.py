from enum import Enum
from typing import Literal, NewType, Union

default_model_name = "default"


class ComponentType(Enum):
    """
    组件类型枚举
    """

    RectangularNode = (
        60003,
        "矩形节点",
    )
    PalletRack = (
        60005,
        "托盘货架",
    )
    AgvRack = (
        60006,
        "AGV货架",
    )
    Asrs = (
        60018,
        "立库",
    )
    PickingRack = (
        60014,
        "挑拣货架",
    )
    AgvAgent = (
        70001,
        "AGV智能体",
    )
    ForkliftAgent = (
        70002,
        "叉车智能体",
    )
    StockAgent = (
        70003,
        "货物智能体",
    )

    def label(self):
        return self.value[1]

    def id(self):
        return self.value[0]

    def id_str(self) -> str:
        return str(self.id())

    def has_id(self, id: Union[str, int]):
        """
        以非严格模式判断id是否相等
        """
        return self.id_str() == str(id)

    def to_dict(self):
        return dict(id=self.id(), label=self.label(), id_str=self.id_str())


class OperationType(Enum):
    """
    操作类型
    """

    Pick = "pick"
    Store = "store"

    def matches(self, operation: Union[str, "OperationType"]):
        return self == operation or self.value == operation


StorageLocationAssignmentStrategy = NewType("StorageLocationAssignmentStrategy", str)
NumberDescend = StorageLocationAssignmentStrategy("按储位编号从大到小")
NumberAscend = StorageLocationAssignmentStrategy("按储位编号从小到大")

RackSelectionStrategy = NewType("RackSelectionStrategy", str)
JobQuantityAscend = RackSelectionStrategy("按作业数量少的货架优先")
DistanceAscend = RackSelectionStrategy("按距离近的货架优先")


TaskType = NewType("TaskType", str)
BatchIn = TaskType("整批入库")
BatchOut = TaskType("整批出库")
ScatterIn = TaskType("零散入库")
ScatterOut = TaskType("零散出库")

TriggerMode = NewType("TriggerMode", str)
ByOrder = TriggerMode("按订单表")
ByEvent = TriggerMode("按事件")

RackType = NewType("RackType", str)

ReplenishmentType = Literal["库区补货", "储位补货"]

LOGIC_TOPO_FILE_EXT = ".logic.gexf"
SCENE_TOPO_FILE_EXT = ".scene.gexf"
TASK_GRAPH_FILE_EXT = ".task_graph.gexf"
PRODUCE_RECIPE_GRAPH_FILE_EXT = ".produce_recipe_graph.gexf"
RACK_GRAPH_FILE_EXT = ".rack_graph.gexf"
NETWORK_FILE_EXT = ".network.gexf"
SQLITE_EXT = ".db"
