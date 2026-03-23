from datetime import datetime
from typing import TYPE_CHECKING, Dict, List, Optional

from ipa.decorator import deprecated
from pydantic import BaseModel
from sqlmodel import Field, SQLModel

from logis.biz.sim.produce import RecipeItemVo
from logis.data_type import DEFAULT_PYDANTIC_MODEL_CONFIG
from logis.event import EventBaseModel
from logis.metric import MetricModel
from logis.metric.influxdb import Point


class BaseEventMetric(EventBaseModel):
    """
    base event metric.
    """

    # 数据所属用户
    user_id: Optional[str] = None

    # 每次仿真有不同的identifier，便于区分
    sim_id: str

    sim_time: Optional[float] = None

    event_time: Optional[float] = Field(exclude=True, default=None)


@deprecated("useless for now")
class SimEventMetric(BaseEventMetric[str], SQLModel, table=False):
    """

    simualtion system metric event.

    """

    __tablename__ = "metric"

    # 下面是一些常规字段
    created_at: datetime = datetime.now()

    updated_at: Optional[datetime] = None

    id: Optional[int] = Field(
        primary_key=True, default=None, sa_column_kwargs={"autoincrement": True}
    )


class PickingStationMetric(BaseEventMetric, MetricModel):
    """
    picking station metric event.
    """

    sim_id: Optional[str] = None

    picking_station_name: Optional[str] = None

    picking_station_id: Optional[str] = None

    working_mode: Optional[str] = None

    @classmethod
    def get_measurement(
        cls, prefix: Optional[str] = None, suffix: Optional[str] = None, sep: str = "/"
    ):
        return sep.join(filter(lambda x: x, [prefix, "picking_station_metric", suffix]))

    def to_influxdb_point(self, measurement: Optional[str] = None):
        p = Point(measurement or self.get_measurement())
        p.tag("event_type", self.event_type)
        p.tag("sim_id", self.sim_id)
        p.tag("picking_station_id", self.picking_station_id)
        p.field("picking_station_name", self.picking_station_name)
        p.field("working_mode", self.working_mode)
        return p


class TaskEventMetric(BaseEventMetric[str], MetricModel):
    """
    task metric event.
    """

    sim_id: Optional[str] = None

    order_id: Optional[str] = None

    task_id: str

    sim_time: Optional[float] = None

    success: Optional[bool] = None

    @classmethod
    def get_measurement(
        cls, prefix: Optional[str] = None, suffix: Optional[str] = None, sep: str = "/"
    ):
        return sep.join(filter(lambda x: x, [prefix, "task_metric", suffix]))

    def to_influxdb_point(self, measurement: Optional[str] = None):
        p = Point(measurement or self.get_measurement())
        p.tag("event_type", self.event_type)
        p.tag("sim_id", self.sim_id)
        p.tag("order_id", self.order_id)
        p.tag("task_id", self.task_id)
        p.field("sim_time", self.sim_time)
        p.field("success", self.success)
        return p


class ReplenishEventMetric(TaskEventMetric):
    """
    replenish event metric.
    """

    destination: Optional[str] = None

    stock_name: Optional[str] = None

    quantity: Optional[int] = None

    unit: Optional[str] = None

    @classmethod
    def get_measurement(
        cls, prefix: Optional[str] = None, suffix: Optional[str] = None, sep: str = "/"
    ):
        return sep.join(filter(lambda x: x, [prefix, "replenish_metric", suffix]))

    def to_influxdb_point(self, measurement: Optional[str] = None):
        p = super().to_influxdb_point(measurement)
        p.tag("destination", self.destination)
        p.tag("stock_name", self.stock_name)
        p.field("quantity", self.quantity)
        p.field("unit", self.unit)
        return p


class StorageLocationMetric(BaseModel, MetricModel):
    """
    storage location metric event.
    """

    sim_id: Optional[str] = None

    storage_location_id: str

    delta_quantity: Optional[float] = None

    stock_name: Optional[str] = None

    stock_unit: Optional[str] = None

    @classmethod
    def get_measurement(
        cls, prefix: Optional[str] = None, suffix: Optional[str] = None, sep: str = "/"
    ):
        return sep.join(
            filter(lambda x: x, [prefix, "storage_location_metric", suffix])
        )

    def to_influxdb_point(self, measurement: Optional[str] = None):
        p = Point(measurement or self.get_measurement())
        p.tag("sim_id", self.sim_id)
        p.tag("storage_location_id", self.storage_location_id)
        p.field("delta_quantity", self.delta_quantity)
        p.field("stock_name", self.stock_name)
        p.field("stock_unit", self.stock_unit)
        return p


class StorageMetric(BaseModel, MetricModel):
    """
    storage metric event.
    """

    sim_id: Optional[str] = None

    storage_id: str

    storage_type: Optional[str] = None

    capacity: Optional[float] = None

    capacity_occupied: Optional[float] = None

    stock_name: Optional[str] = None

    stock_unit: Optional[str] = None

    @classmethod
    def get_measurement(
        cls, prefix: Optional[str] = None, suffix: Optional[str] = None, sep: str = "/"
    ):
        return sep.join(filter(lambda x: x, [prefix, "storage_metric", suffix]))

    def to_influxdb_point(self, measurement: Optional[str] = None):
        p = Point(measurement or self.get_measurement())
        p.tag("sim_id", self.sim_id)
        p.tag("storage_id", self.storage_id)
        p.tag("storage_type", self.storage_type)
        p.field("capacity", self.capacity)
        p.field("capacity_occupied", self.capacity_occupied)
        p.field("stock_name", self.stock_name)
        p.field("stock_unit", self.stock_unit)
        return p


class AgentEventMetric(BaseEventMetric[str], MetricModel):
    """
    agent metric event.
    """

    sim_id: Optional[str] = None

    agent_id: int

    agent_type: Optional[str] = None

    order_id: Optional[str] = None
    task_id: Optional[str] = None

    sim_time: Optional[float] = None

    @classmethod
    def get_measurement(
        cls, prefix: Optional[str] = None, suffix: Optional[str] = None, sep: str = "/"
    ):
        return sep.join(filter(lambda x: x, [prefix, "agent_metric", suffix]))

    def to_influxdb_point(self, measurement: Optional[str] = None):
        p = Point(measurement or self.get_measurement())
        p.tag("sim_id", self.sim_id)
        p.tag("event_type", self.event_type)
        p.tag("agent_id", self.agent_id)
        p.tag("agent_type", self.agent_type)
        p.field("sim_time", self.sim_time)
        p.tag("order_id", self.order_id).tag("task_id", self.task_id)
        return p


class SimMetric(BaseModel, MetricModel):
    """
    simulation metric event.
    """

    sim_id: str
    model_name: Optional[str] = None
    sim_abs_time: Optional[float] = None
    event_type: str

    @classmethod
    def get_measurement(
        cls, prefix: Optional[str] = None, suffix: Optional[str] = None, sep: str = "/"
    ):
        return sep.join(filter(lambda x: x, [prefix, "sim_metric", suffix]))

    def to_influxdb_point(self, measurement: Optional[str] = None):
        p = Point(measurement or self.get_measurement())
        p.tag("sim_id", self.sim_id)
        p.tag("event_type", self.event_type)
        p.field("model_name", self.model_name)
        p.field("sim_abs_time", self.sim_abs_time)
        return p


class SimQuery(BaseModel):
    """
    模拟查询条件
    """

    sim_id: str


class StorageDeviceQuery(SimQuery):
    """
    存储设备查询条件
    """

    sim_id: str
    rack_ids: Optional[List[str]] = None
    cell_ids: Optional[List[str]] = None


class TransportDeviceQuery(SimQuery):
    """
    运输设备查询条件
    """

    sim_id: str


class InventoryChange(BaseModel):
    """
    库存变化
    """

    stock_name: str
    stock_unit: str
    delta_quantity: float


class ContainerWatchInfo(BaseModel):
    """
    容器监控信息
    """

    parent_id: Optional[str] = None
    id: str
    capacity: Optional[float] = None
    init_level: Optional[float] = None
    level: Optional[float] = None


class AgentWatchInfo(BaseModel):
    """
    智能体工作信息
    """

    agent_id: int
    agent_type: Optional[str] = None
    order_id: Optional[str] = None
    task_id: Optional[str] = None
    duration: Optional[float] = None
    acquired_at: Optional[float] = None
    released_at: Optional[float] = None

    model_config = DEFAULT_PYDANTIC_MODEL_CONFIG


class TaskWatchInfo(BaseModel):
    """
    任务监控信息
    """

    order_id: Optional[str] = None
    task_id: str
    duration: Optional[float] = None
    # None: 未完成,False: 延迟完成,True: 按时完成
    on_time: Optional[bool] = None

    started_at: Optional[float] = None
    finished_at: Optional[float] = None
    success: Optional[bool] = None

    model_config = DEFAULT_PYDANTIC_MODEL_CONFIG


class ReplenishTaskWatchInfo(TaskWatchInfo):
    """
    补货任务监控信息
    """

    destination: Optional[str] = None
    stock_name: str
    quantity: float
    unit: Optional[str] = None

    model_config = DEFAULT_PYDANTIC_MODEL_CONFIG


class OrderWatchInfo(BaseModel):
    """
    订单监控信息
    """

    order_id: str
    order_type: Optional[str] = None
    duration: Optional[float] = None
    # None: 未完成,False: 延迟完成,True: 按时完成
    on_time: Optional[bool] = None

    started_at: Optional[float] = None
    finished_at: Optional[float] = None

    model_config = DEFAULT_PYDANTIC_MODEL_CONFIG


class StockoutWatchInfo(BaseModel):
    """
    缺货监控信息
    """

    stockout_rate: Optional[float] = None
    stockout_count: Optional[int] = None
    retrieve_count: Optional[int] = None


class StorageLocationTurnoverInfo(BaseModel):
    """
    储位周转信息
    """

    # 周转数量
    turnover_quantity: float

    # 初始库存
    init_level: Optional[float] = None
    # 期末库存
    final_level: Optional[float] = None

    @property
    def turnover_rate(self) -> float:
        y = (self.init_level + self.final_level) / 2
        return self.turnover_quantity / y if y else 0
        # return self.turnover_quantity / self.capacity if self.capacity else 0


from logis.data_type import Time


class SimDurationInfo(BaseModel):
    """
    模拟运行时间信息
    """

    sim_id: str
    real: Optional[Time] = None
    sim: Optional[Time] = None
    sim_start_time: Optional[datetime] = None
    sim_end_time: Optional[datetime] = None


class RecipeItemVoAbnormalNum(RecipeItemVo):
    """配方物品异常信息"""

    abnormal_num: int  # 异常数量


class ProductionAbnormalMetric(BaseModel):
    """生产异常信息数据结构"""

    workstation_name: str  # 工作站名称
    workstation_id: Optional[str] = None  # 工作站ID
    materials: Optional[List[RecipeItemVoAbnormalNum]] = None  # 异常发生时的原材料信息


class WorkstationMetric(BaseModel):
    """工作站信息数据结构"""

    sim_id: Optional[str] = None
    workstation_id: str  # 工作站ID
    workstation_name: str  # 工作站名称
    processing_time: float  # 加工时间（秒）
    input_materials: Optional[List[RecipeItemVo]] = None  # 输入材料列表
    output_materials: Optional[List[RecipeItemVo]] = None  # 输出材料列表
    total_processing_time: float  # 使用时长
    downtime_duration: float = 0  # 停机时长（秒）


class ProductionLineMetric(BaseModel):
    """产线信息数据结构"""

    sim_id: Optional[str] = None
    production_line_name: str  # 产线名称
    production_beat: float  # 生产节拍（秒）
    total_production: int = 0  # 仿真周期生产总量
    product_unit: Optional[str] = "件"  # 产品单位
    capacity_utilization_rate: float = 0  # 产能利用率
    total_processing_time: float = 0  # 产线加工总时长（秒）
    average_utilization_rate: float = 0  # 平均利用率
    average_usage_duration: float = 0  # 平均使用时长（秒）
    workstation_num: int  # 工作站数量
    production_abnormal_list: Optional[List[ProductionAbnormalMetric]] = (
        None  # 生产异常列表
    )
    workstation_list: Optional[List[WorkstationMetric]] = None  # 工作站列表
