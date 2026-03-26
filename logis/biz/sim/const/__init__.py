from enum import Enum
from typing import Literal, NewType, TypeAlias, Union

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


LegencyStorageSelectionStrategyName: TypeAlias = Literal[
    "按储位编号从大到小",
    "按储位编号从小到大",
    "按作业数量少的货架优先",
    "按距离近的货架优先",
]


class StorageSelectionStrategy(Enum):
    """
    存储选择策略枚举，此枚举试图统一并兼容历史逻辑
    """

    BusyLevelAscend = "按作业数量少的优先"
    DistanceAscend = "按距离近的优先"
    NumberAscend = "按编号从小到大"
    NumberDescend = "按编号从大到小"
    Custom = "自定义"

    def matches(
        self,
        strategy: Union[
            "StorageSelectionStrategy", LegencyStorageSelectionStrategyName
        ],
    ):
        # 下面有一些历史兼容逻辑
        if strategy == "按储位编号从大到小":
            return self == StorageSelectionStrategy.NumberDescend
        if strategy == "按储位编号从小到大":
            return self == StorageSelectionStrategy.NumberAscend
        if strategy == "按作业数量少的货架优先":
            return self == StorageSelectionStrategy.BusyLevelAscend
        if strategy == "按距离近的货架优先":
            return self == StorageSelectionStrategy.DistanceAscend
        return self == strategy or self.value == strategy


AgentSelectionStrategyName: TypeAlias = Literal["距离近优先", "空闲优先", "自定义"]
AgentIdleStrategyOption: TypeAlias = Literal["返回到归属地位置", "停留在原地", "自定义"]
GoHomeStrategyFrequency: TypeAlias = Literal["每次", "如果无其他任务"]


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
