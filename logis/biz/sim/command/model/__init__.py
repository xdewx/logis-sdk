from pathlib import Path
from typing import Literal, Optional

from pydantic import BaseModel

from logis.data_type.base import DEFAULT_PYDANTIC_MODEL_CONFIG


class SetupArgs(BaseModel):
    # 是否开启硬编码测试
    enable_hardcode_test: bool = False

    # 是否将其他智能体视为障碍物
    agent_as_obstacle: Optional[bool] = None
    # 是否将货架视为障碍物
    rack_as_obstacle: Optional[bool] = None

    # 是否在退出任务前校验货物量是否一致
    disable_verify_stock_quantity_before_exit: bool = False

    # 拣选货架是否开启储位
    enable_picking_rack_cell: bool = False

    # 是否打印版本号
    version: bool = False

    max_sim_time: Optional[float] = None
    max_run_time: Optional[float] = None

    server_version: Literal["v1", "v2"] = "v2"
    host: str = "127.0.0.1"
    port: int = 8765

    model_config = DEFAULT_PYDANTIC_MODEL_CONFIG

    disable_metric: bool = False
    influxdb_config: Optional[Path] = None

    filter_order_type: Optional[str] = None
    filter_order_offset: Optional[int] = None
    filter_order_limit: Optional[int] = None

    echo: bool = False
    with_memory_db: bool = False
    db_url: Optional[str] = None
    enable_decorators: bool = False
    model: Optional[str] = None
    model_path: Optional[Path] = None
    level: Optional[str] = "WARNING"
    with_node_listener: bool = False
    enable_mapf: bool = False
    with_model_picker: bool = False

    debug: bool = False

    def parse_db_url(self) -> Optional[str]:
        if self.with_memory_db:
            return "sqlite:///:memory:"
        return self.db_url
