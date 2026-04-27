from pathlib import Path
from typing import Literal, Optional

from pydantic import BaseModel

from logis.data_type.base import DEFAULT_PYDANTIC_MODEL_CONFIG


class SetupArgs(BaseModel):
    enable_hardcode_test: bool = False
    """
    是否开启硬编码测试
    """
    agent_as_obstacle: Optional[bool] = None
    """
    是否将其他智能体视为障碍物
    """
    rack_as_obstacle: Optional[bool] = None
    """
    是否将货架视为障碍物
    """

    disable_verify_stock_quantity_before_exit: bool = False
    """
    是否禁用：在退出任务前校验货物量是否一致
    """

    # 拣选货架是否开启储位
    enable_picking_rack_cell: bool = False
    """
    是否开启：拣选货架是否开启储位
    """

    version: bool = False
    """
    是否打印版本号
    """

    max_sim_time: Optional[float] = None
    """
    最大模拟时间, 单位秒
    """
    max_run_time: Optional[float] = None
    """
    最大运行时间, 单位秒
    """

    server_version: Literal["v1", "v2"] = "v2"
    """
    所使用的服务器版本，默认v2
    """
    host: str = "127.0.0.1"
    port: int = 8765

    model_config = DEFAULT_PYDANTIC_MODEL_CONFIG

    disable_metric: bool = False
    """
    是否禁用：收集指标
    """
    influxdb_config: Optional[Path] = None
    """
    InfluxDB配置文件路径
    """

    filter_order_type: Optional[str] = None
    """
    所过滤的订单类型
    """
    filter_order_offset: Optional[int] = None
    """
    所过滤的订单偏移量
    """
    filter_order_limit: Optional[int] = None
    """
    所限制执行的订单数量
    """

    echo: bool = False
    with_memory_db: bool = False
    db_url: Optional[str] = None
    enable_decorators: bool = False
    model: Optional[str] = None
    """
    案例名称
    """
    model_path: Optional[Path] = None
    """
    案例所在目录
    """
    level: Optional[str] = "WARNING"
    """
    日志级别，默认WARNING
    """
    with_node_listener: bool = False
    enable_mapf: bool = False
    with_model_picker: bool = False
    """
    是否开启：案例选择器
    """

    debug: bool = False
    """
    是否开启：调试模式
    """

    def parse_db_url(self) -> Optional[str]:
        if self.with_memory_db:
            return "sqlite:///:memory:"
        return self.db_url
