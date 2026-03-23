import asyncio
from pathlib import Path
from typing import Any, Dict, Generic, TypeVar, Union

import simpy
from networkx import DiGraph
from pydantic import AliasChoices
from pyee import EventEmitter

from logis.data_type import DEFAULT_PYDANTIC_MODEL_CONFIG, ComponentId, Point, TmpId
from logis.iface import Storable
from logis.util.websocket_util import (
    ClientConnection,
    ServerConnection,
    is_websocket_closed,
)

from .component import *

T = TypeVar("T")

LocationType = Union[Point, Storable]


class SimMetadata(BaseModel):
    """
    仿真元数据
    """

    sim_id: Optional[str] = Field(
        validation_alias=AliasChoices("sim_id", "simId"),
        default=None,
    )
    model_path: Optional[Path] = Field(
        validation_alias=AliasChoices("model_path", "modelPath"), default=None
    )
    # 历史逻辑仅支持单个仿真的同步模式，新逻辑新增完全异步模式
    mode: Optional[Literal["sync", "async"]] = None

    user_id: Optional[str] = Field(
        validation_alias=AliasChoices("user_id", "user"), default=None
    )

    client_version: Optional[str] = Field(
        validation_alias=AliasChoices("client_version", "version"), default=None
    )

    server_version: Optional[str] = Field(
        validation_alias=AliasChoices("server_version", "serverVersion"), default=None
    )

    send_step_info_realtime: Optional[bool] = Field(
        None,
        validation_alias=AliasChoices(
            "send_step_info_realtime", "sendStepInfoRealtime"
        ),
    )

    model_config = DEFAULT_PYDANTIC_MODEL_CONFIG


class SimConfig(SimMetadata):
    model_config = DEFAULT_PYDANTIC_MODEL_CONFIG

    json_path: Optional[str] = None
    excel_path: Optional[str] = None
    result_path: Optional[str] = None

    # 实际最长运行时间，单位s，默认不限时
    max_run_time: Optional[float] = None
    # 最大模拟时间，默认不限时
    max_sim_time: Optional[float] = None

    def resolve_model_name(self) -> Optional[str]:
        from logis.biz.sim.path_util import resolve_model_name

        return resolve_model_name(self.model_path)

    def resolve_result_path(self):
        if self.result_path:
            return Path(self.result_path)
        from logis.biz.sim.path_util import resolve_result_path

        return resolve_result_path(self.model_path)

    def resolve_excel_path(self) -> Optional[Path]:
        if self.excel_path:
            return Path(self.excel_path)
        from logis.biz.sim.path_util import resolve_excel_path

        return resolve_excel_path(self.model_path)

    def resolve_json_path(self) -> Optional[Path]:
        if self.json_path:
            return Path(self.json_path)
        from logis.biz.sim.path_util import resolve_json_path

        return resolve_json_path(self.model_path)


class OldSimEvent(SimMetadata):
    """
    旧版仿真事件结构体，包含了仿真过程中产生的事件可能用到的所有字段
    """

    # 下面的都是历史结构体，所有的字段融合在一起，后续逐步使用泛型代替
    entity_id: Optional[TmpId] = Field(
        validation_alias=AliasChoices("entity_id", "agent_id", "id"), default=None
    )
    # 智能体类型
    entity_type: Optional[ComponentId] = None
    # 起始位置
    start_pos: Optional[List[float]] = None
    start_point: Optional[Point] = None
    # 结束位置
    end_pos: Optional[List[float]] = None
    end_point: Optional[Point] = None
    # 时长
    duration: Optional[Union[int, float]] = None
    # FIXME:名字叫货架ID，但实际上存的全是stock_id
    payload_id: Optional[TmpId] = Field(
        validation_alias=AliasChoices("shelf_id", "payload_id"), default=None
    )
    rack_id: Optional[TmpId] = None
    # 货物载体ID
    carrier_id: Optional[TmpId] = None

    init_stock: Optional[bool] = None
    stock: Optional[Any] = None
    stock_id: Optional[TmpId] = None

    model_config = DEFAULT_PYDANTIC_MODEL_CONFIG


class SimEvent(OldSimEvent, Generic[T]):
    """
    仿真过程中产生的事件

    此结构体起初是个大杂烩，包含了仿真过程中产生的事件可能用到的所有字段，后来逐步改造成泛型

    TODO: 这里只所以还继承OldSimEvent，是因为历史代码里有很多地方已经用了SimEvent\\
    实际上是OldSimEvent，后续会逐步替换掉并去除这里的继承
    """

    source_id: Optional[TmpId] = Field(
        validation_alias=AliasChoices("source_id", "src"), default=None
    )

    # 仿真事件发生的时间
    time: Optional[Union[int, float]] = Field(default=None)
    # 事件类型
    event_type: Optional[str] = Field(
        validation_alias=AliasChoices("eventType", "event_type", "type"), default=None
    )
    # 事件数据
    data: Optional[T] = None
    extra: Optional[Dict[str, Any]] = None

    model_config = DEFAULT_PYDANTIC_MODEL_CONFIG
    # 真实时间戳
    timestamp: Optional[float] = None

    def to_config(self):
        return SimConfig(
            sim_id=self.sim_id,
            model_path=self.model_path,
            mode=self.mode,
            send_step_info_realtime=self.send_step_info_realtime,
        )


class SimContext(SimMetadata):
    """
    仿真上下文
    """

    # 正常完成的信号
    __finish_event__: Optional[simpy.Event] = None
    # 终止仿真的信号
    __terminate_event__: Optional[simpy.Event] = None
    env: simpy.Environment = Field(default_factory=simpy.Environment)
    event_emitter: EventEmitter = Field(default_factory=EventEmitter)
    sim_config: Optional[SimConfig] = None
    errors: List[str] = Field(default_factory=list)
    network: DiGraph = Field(default_factory=DiGraph)
    ws_conn: Union[ClientConnection, ServerConnection, None] = None
    event_loop: Optional[asyncio.BaseEventLoop] = None

    extra: Optional[Dict[str, Any]] = None

    model_config = DEFAULT_PYDANTIC_MODEL_CONFIG

    @property
    def terminate_event(self) -> simpy.Event:
        """
        仿真终止事件
        """
        assert self.env, "环境未初始化"
        env = self.env
        if self.__terminate_event__ is None:
            self.__terminate_event__ = env.event()
        return self.__terminate_event__

    @property
    def finish_event(self) -> simpy.Event:
        """
        仿真完成事件
        """
        assert self.env, "环境未初始化"
        env = self.env
        if self.__finish_event__ is None:
            self.__finish_event__ = env.event()
        return self.__finish_event__

    def trigger_finish_event_if_not(self):
        """
        如果仿真完成事件还没有被触发，就触发它
        """
        if not self.finish_event.triggered:
            self.finish_event.succeed()

    def trigger_terminate_event_if_not(self):
        """
        如果仿真终止事件还没有被触发，就触发它
        """
        if not self.terminate_event.triggered:
            self.terminate_event.succeed()

    def is_terminated(self):
        """
        判断仿真是否已被终止
        """
        return self.terminate_event.triggered

    def is_finished(self):
        """
        判断仿真是否已完成
        """
        return self.finish_event.triggered

    def is_over(self):
        """
        判断仿真是否结束
        """
        if self.ws_conn and (is_websocket_closed(self.ws_conn)):
            return True
        return self.is_finished() or self.is_terminated()

    def resolve_sim_id(self) -> Optional[str]:
        """
        优先读取sim_config中的id，其次是本结构体中的id
        """
        return (self.sim_config.sim_id if self.sim_config else None) or self.sim_id

    def resolve_model_path(self) -> Optional[Path]:
        """
        优先读取sim_config中的model_path，其次是本结构体中的model_path
        """
        return (
            self.sim_config.model_path if self.sim_config else None
        ) or self.model_path

    def resolve_model_name(self) -> Optional[str]:
        path = self.resolve_model_path()
        return path.name if path else None
