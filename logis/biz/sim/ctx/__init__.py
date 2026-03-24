import asyncio
import logging
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Callable, Dict, Optional, Type
from uuid import uuid4

import simpy
from networkx import DiGraph
from sqlmodel import Session, create_engine

from logis.biz.sim import *
from logis.biz.sim.command.model import SetupArgs
from logis.biz.sim.const import SQLITE_EXT
from logis.biz.sim.data_type import SimContext
from logis.biz.sim.graph import IPathGraph

# TODO: metric是否有必要放到sdk中
from logis.biz.sim.metric import ProductionLineMetric
from logis.biz.sim.path_util import sim_data_dir
from logis.conf.app import IAppConfig
from logis.ctx import Context as BaseContext
from logis.logging import LoggerBuilder
from logis.metric import IMetricCollector
from logis.task.manager import TaskGraph


class Context(BaseContext):
    """
    仿真上下文,按照协程隔离
    """

    ID_SIM_CTX_MAP: Dict[str, SimContext] = defaultdict()
    ID_LOGGER_MAP: Dict[str, logging.Logger] = defaultdict()
    _is_simulating = False
    _simulation_lock = asyncio.Lock()

    APP_CONFIG: IAppConfig

    @classmethod
    def data_dir(cls, sim_id: Optional[str] = None) -> Path:
        """
        获取当前仿真案例所对应的数据目录
        """
        sim_id = sim_id or cls.sim_id()
        d = sim_data_dir(sim_id, data_dir=cls.APP_CONFIG.get_data_dir())
        d.mkdir(parents=True, exist_ok=True)
        return d

    @classmethod
    def data_report(
        cls, v=None, default_factory: Callable[[], "IDataReport"] = None
    ) -> "IDataReport":
        """
        获取当前仿真案例所对应的data report
        """
        key = "__data_report__"
        if v is not None:
            cls.set(key, v)
        return cls.get(key, create=True, default_factory=default_factory)

    @classmethod
    def logger_builder(cls, name: str, sim_id: Optional[str] = None) -> LoggerBuilder:
        level = cls.setup_args().level or "INFO"
        sim_id = sim_id or cls.sim_id() or ""
        return (
            LoggerBuilder()
            # 避免同名冲突
            .name(f"{sim_id}_{name}")
            .dir(cls.data_dir(sim_id=sim_id) / "logs")
            .level(level.upper())
            .backup_count(2)
        )

    @classmethod
    def logger(cls, sim_id: Optional[str] = None) -> logging.Logger:
        """
        获取当前仿真案例所对应的logger，如果当前没有仿真案例，则返回默认logger
        """
        sim_id = sim_id or cls.sim_id()
        if not sim_id:
            return cls.APP_CONFIG.get_app_logger()

        log = cls.ID_LOGGER_MAP.get(sim_id, None)
        if log:
            return log

        log = (
            cls.logger_builder(name=sim_id, sim_id=sim_id)
            .add_handler(logging.StreamHandler)
            .add_handler(
                logging.handlers.RotatingFileHandler,
                filename="info.log",
                level=logging.DEBUG,
            )
            .add_handler(
                logging.handlers.RotatingFileHandler,
                filename="warning.log",
                level=logging.WARNING,
                filters=[lambda record: record.levelno == logging.WARNING],
            )
            .add_handler(
                logging.handlers.RotatingFileHandler,
                filename="error.log",
                level=logging.ERROR,
            )
            .build()
        )
        cls.ID_LOGGER_MAP[sim_id] = log
        return log

    @classmethod
    def helper(cls) -> Dict[str, list]:
        key = "__helper__"
        return cls.get(key, default_factory=lambda: defaultdict(list), create=True)

    @classmethod
    def storage_manager(
        cls, v: Optional["IStorageManager"] = None
    ) -> "IStorageManager":
        key = "__storage_manager__"
        if v is not None:
            cls.set(key, v)
        return cls.get(key)

    @classmethod
    def add_error(cls, msg: str, sim_id: Optional[str] = None):
        cls.get_sim_context(sim_id=sim_id).errors.append(msg)

    @classmethod
    def sim_abs_start_time(cls, v: Optional[datetime] = None) -> datetime:
        """
        仿真开始的绝对时间,也就是订单表中最早任务的开始时间，也是逻辑0时刻
        """
        key = "__sim_abs_start_time__"
        return cls.get(key, default=v, create=True)

    @classmethod
    def sim_db_engine(cls, *args, **kwargs):

        def _new_db_engine():
            sim_id = cls.sim_id()
            assert sim_id, "仿真ID缺失"
            d = sim_data_dir(sim_id)
            d.mkdir(parents=True, exist_ok=True)
            db_file = d / f"{sim_id}{SQLITE_EXT}"
            return create_engine(f"sqlite:///{db_file.resolve().as_posix()}")

        key = "__db_engine_by_sim_id__"
        return cls.get(key, default_factory=_new_db_engine, create=True)

    @classmethod
    def sim_db_session(cls, sim_id: Optional[str] = None):
        return Session(cls.sim_db_engine(sim_id=sim_id))

    @classmethod
    def error_message(cls, sim_id: Optional[str] = None) -> str:
        return "\n".join((cls.get_sim_context(sim_id=sim_id).errors) or [])

    @classmethod
    def path_graph(cls, v=None) -> Optional[IPathGraph]:
        key = "__path_graph__"
        if v is not None:
            cls.set(key, v)
        return cls.get(key)

    @classmethod
    def result_generator(cls, v=None) -> Optional["IResultGenerator"]:
        key = "__result_generator__"
        if v is not None:
            cls.set(key, v)
        return cls.get(key)

    @classmethod
    def unit_manager(cls, v=None) -> Optional["IUnitManager"]:
        key = "__unit_manager__"
        if v is not None:
            cls.set(key, v)
        return cls.get(key)

    @classmethod
    def json_parser(cls, v=None) -> Optional["IJsonParser"]:
        key = "__json_parser__"
        if v is not None:
            cls.set(key, v)
        return cls.get(key)

    @classmethod
    def excel_parser(cls, v=None) -> Optional["IExcelParser"]:
        key = "__excel_parser__"
        if v is not None:
            cls.set(key, v)
        return cls.get(key)

    @classmethod
    def order_manager(cls, v=None) -> Optional["IOrderManager"]:
        key = "__order_manager__"
        if v is not None:
            cls.set(key, v)
        return cls.get(key)

    @classmethod
    def resource_manager(cls, v=None) -> Optional["IResourceManager"]:
        key = "__resource_manager__"
        if v is not None:
            cls.set(key, v)
        return cls.get(key)

    @classmethod
    def get_sim_context(
        cls, auto_create=False, sim_id: Optional[str] = None
    ) -> Optional[SimContext]:
        sim_id = sim_id or cls.sim_id()
        ctx = cls.ID_SIM_CTX_MAP.get(sim_id)
        if ctx is None and auto_create is True:
            sim_id = str(uuid4()) if sim_id is None else sim_id
            ctx = SimContext(sim_id=sim_id)
            cls.set_sim_context(ctx)
        assert sim_id, "sim_id缺失，无法找到对应上下文"
        return ctx

    @classmethod
    def set_sim_context(cls, ctx: SimContext):
        sim_id = ctx.resolve_sim_id()
        assert sim_id, "仿真上下文未初始化sim_id"
        cls.sim_id(sim_id)
        cls.ID_SIM_CTX_MAP[sim_id] = ctx

    @classmethod
    def get_env(cls, auto_create=True, sim_id: Optional[str] = None):
        ctx = cls.get_sim_context(auto_create=auto_create, sim_id=sim_id)
        return ctx.env if ctx else None

    @classmethod
    def sim_id(cls, v: Optional[str] = None, force: bool = False) -> Optional[str]:
        __key__ = "__sim_id__"
        last_id = cls.get(__key__)
        if (not force) and v is not None:
            assert (
                last_id is None or last_id == v
            ), f"上下文出现了问题，联系开发者处理: {last_id} != {v}"
            cls.set(__key__, v)
        return cls.get(__key__)

    @classmethod
    def setup_args(cls, args: Optional[SetupArgs] = None) -> SetupArgs:
        key = "__setup_args__"
        if args:
            setattr(cls, key, args)
        return getattr(cls, key, SetupArgs())

    @classmethod
    def network(cls, sim_id: Optional[str] = None) -> DiGraph:
        return cls.get_sim_context(sim_id=sim_id).network

    @classmethod
    def task_graph(cls) -> TaskGraph:
        key = "__task_graph__"
        return cls.get(key, default_factory=TaskGraph, create=True)

    @classmethod
    def rack_graph(cls) -> DiGraph:
        key = "__rack_graph__"
        return cls.get(key, default_factory=DiGraph, create=True)

    @classmethod
    def terminate_event(cls, sim_id: Optional[str] = None) -> simpy.Event:
        sim_id = sim_id or cls.sim_id()
        ctx = cls.get_sim_context(auto_create=False, sim_id=sim_id)
        assert ctx, f"sim_id={sim_id} 对应的上下文不存在"
        return ctx.terminate_event

    @classmethod
    def finish_event(cls, sim_id: Optional[str] = None) -> simpy.Event:
        sim_id = sim_id or cls.sim_id()
        ctx = cls.get_sim_context(auto_create=False, sim_id=sim_id)
        assert ctx, f"sim_id={sim_id} 对应的上下文不存在"
        return ctx.finish_event

    @classmethod
    def metric_collector(
        cls, default_factory: Optional[Type[IMetricCollector]] = None
    ) -> "IMetricCollector":
        key = "__metric_collector__"
        return cls.get(key, default_factory=default_factory, create=True)

    @classmethod
    def reset(cls, sim_id: Optional[str] = None):
        """
        重置上下文
        """
        sim_id = sim_id or cls.sim_id()
        cls.ID_SIM_CTX_MAP.pop(sim_id, None)
        cls.ID_LOGGER_MAP.pop(sim_id, None)
        # cls.logger().info("reset context:%s", cls.sim_id())
        super().reset()

    @classmethod
    def production_line_metrics(
        cls, v: Optional[Dict[str, "ProductionLineMetric"]] = None
    ) -> Dict[str, "ProductionLineMetric"]:
        """
        管理所有产线的指标数据
        """
        key = "__production_line_metrics__"
        if v is not None:
            cls.set(key, v)
        return cls.get(key, default_factory=dict, create=True)

    @classmethod
    def production_line_metric(
        cls, line_name: str, v: Optional["ProductionLineMetric"] = None
    ) -> Optional["ProductionLineMetric"]:
        """
        获取或设置特定产线的指标数据
        """
        metrics = cls.production_line_metrics()
        if v is not None:
            metrics[line_name] = v
        return metrics.get(line_name)

    @classmethod
    def is_simulating(cls, v: Optional[bool] = None) -> bool:
        """
        获取或设置仿真状态标志位

        Args:
            v: 如果提供，则设置仿真状态；否则返回当前状态

        Returns:
            当前仿真状态
        """
        if v is not None:
            cls._is_simulating = v
        return cls._is_simulating

    @classmethod
    async def try_set_simulating(cls) -> bool:
        """
        尝试设置仿真状态（原子操作，带锁保护）

        Returns:
            True 表示设置成功，False 表示已有仿真在进行
        """
        async with cls._simulation_lock:
            if cls._is_simulating:
                return False
            cls._is_simulating = True
            return True
