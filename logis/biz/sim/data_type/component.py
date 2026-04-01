import enum
from typing import List, Literal, Optional, TypeAlias

from pydantic import BaseModel, Field


class ComponentConfigItem(BaseModel):
    """
    组件配置项，用于前端展示和后端处理
    """

    # 中文名
    label: Optional[str] = None
    # 描述
    description: Optional[str] = None
    # 类型编码
    type_id: str
    # 加载器，用于指导后端解析组件
    loader: Optional[str] = None
    # 是否卸载，用于卸载已加载的组件
    unload: bool = False

    # 是否启用配置
    enabled: bool = True


class ComponentConfig(BaseModel):
    """
    组件配置
    """

    entity_list: List[ComponentConfigItem] = Field(default_factory=list)


class BlueprintKind(enum.Enum):
    """
    蓝图的类型，如果不够用，可以修改此类或者继承并添加新的类型
    """

    CODE = "code"
    DUMMY = "dummy"
    SOURCE = "source"
    ENTER = "enter"
    EXIT = "exit"
    SINK = "sink"
    ASSEMBLER = "assembler"
    DELAY = "delay"
    EVENT = "event"
    GOODS_TO_PERSON = "goods_to_person"
    PRODUCER = "producer"
    WORK_STATION = "work_station"
    # 最初是资源池、货架组、后来发现二者可以统称为资源集，TODO：后续考虑完全统一
    RESOURCE_SET = "resource_set"
    RESOURCE_POOL = "resource_pool"
    TRANSPORT = "transport"

    RACK_SYSTEM = "rack_system"
    RACK = "rack"
    AGV_RACK = "agv_rack"
    PALLET_RACK = "pallet_rack"
    PICKING_RACK = "picking_rack"
    ASRS = "asrs"
    REPOSITORY = "repository"

    CONVEYOR_BELT = "conveyor_belt"
    TURNING_STATION = "turning_station"
    PATH = "path"
    GRID = "grid"
    POINT_NODE = "point_node"
    RECTANGULAR_NODE = "rectangular_node"

    AGENT = "agent"
    AGV = "agv"
    STOCK = "stock"
    FORKLIFT = "forklift"
