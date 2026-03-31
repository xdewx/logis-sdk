import logging
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Dict, Optional, Type

import simpy
from networkx import DiGraph

from logis.metric import MetricModelType
from logis.task import TaskGraph

from .base import *

if TYPE_CHECKING:
    from ..command.model import SetupArgs
    from ..ctx import Context
    from ..data_type import SimContext


class ISimProxy(ABC):
    """
    仿真模块接口
    """

    @property
    @abstractmethod
    def data_report(self) -> Optional["IDataReport"]:
        pass

    @property
    @abstractmethod
    def log(self) -> logging.Logger:
        pass

    @property
    @abstractmethod
    def json_parser(self) -> Optional["IJsonParser"]:
        pass

    @property
    @abstractmethod
    def result_generator(self) -> Optional["IResultGenerator"]:
        """获取结果生成器（子类需实现）"""
        pass

    @property
    @abstractmethod
    def storage_manager(self) -> Optional["IStorageManager"]:
        """获取存储管理器（子类需实现）"""
        pass

    @property
    @abstractmethod
    def network(self) -> DiGraph:
        """获取网络模块（子类需实现）"""
        pass

    @property
    def env(self) -> simpy.Environment:
        assert self.sim_ctx is not None, "sim_ctx is None"
        return self.sim_ctx.env

    @property
    def sim_id(self) -> str:
        return self.context.sim_id()

    @property
    def context(self) -> Type["Context"]:
        from ..ctx import Context

        return Context

    @property
    @abstractmethod
    def task_graph(self) -> TaskGraph:
        """获取任务图（子类需实现）"""
        pass

    @property
    @abstractmethod
    def rack_graph(self) -> DiGraph:
        """获取机架图（子类需实现）"""
        pass

    @property
    @abstractmethod
    def sim_ctx(self) -> Optional["SimContext"]:
        """获取仿真上下文（子类需实现）"""
        pass

    @property
    def debug(self) -> bool:
        """获取调试模式标识"""
        return self.setup_args.debug

    @property
    @abstractmethod
    def setup_args(self) -> "SetupArgs":
        """获取启动参数（子类需实现）"""
        pass

    def start_timing_if_not(self, key: str):
        """
        如果还没有开始计时就从现在开始计时

        Args:
            key: 时长键
        """
        from ..ctx import Context

        return Context.start_timing_if_not(key, now=self.env.now)

    def stop_timing(self, key: str):
        """
        停止计时

        Args:
            key: 时长键
        """
        from ..ctx import Context

        return Context.stop_timing(key, now=self.env.now)

    @abstractmethod
    def collect_metric(self, metric: MetricModelType):
        """
        收集指标数据（子类需实现）
        Args:
            metric: 指标模型
        """
        pass

    @property
    def logic_graph(self) -> Optional[DiGraph]:
        """基于 json_parser 实现的逻辑图"""
        x = self.json_parser
        return x.logic_graph if x else None

    @property
    def produce_recipe_graph(self) -> Optional[DiGraph]:
        """基于 json_parser 实现的生产配方图"""
        x = self.json_parser
        return x._produce_recipe_graph if x else None

    @property
    def id_instance_map(self) -> Optional[Dict[str, Any]]:
        """基于 json_parser 实现的ID实例映射"""
        x = self.json_parser
        return x.object_map if x else None

    @property
    def is_sim_over(self):
        """
        判断仿真是否已结束，无论是否正常结束
        """
        ctx = self.sim_ctx
        assert ctx, "仿真上下文未初始化"
        return ctx.is_over()

    @property
    def is_sim_terminated(self):
        """
        判断仿真是否已终止
        """
        ctx = self.sim_ctx
        assert ctx, "仿真上下文未初始化"
        return ctx.is_terminated()

    @property
    def ws_conn(self):
        """获取WebSocket连接（基于 sim_ctx 的默认实现，子类可重写）"""
        ctx = self.sim_ctx
        return ctx.ws_conn if ctx else None

    @property
    def event_loop(self):
        ctx = self.sim_ctx
        return ctx.event_loop if ctx else None
