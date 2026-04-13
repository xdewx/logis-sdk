import copy
import logging
from abc import ABCMeta, abstractmethod
from queue import Queue
from threading import Lock
from typing import (
    Generator,
    Iterable,
    List,
    Literal,
    Optional,
    Protocol,
    runtime_checkable,
)

from pydantic import BaseModel, Field

from logis.biz.sim.agent import IAgent
from logis.data_type import DEFAULT_PYDANTIC_MODEL_CONFIG, Point, get_time, get_time_3d

from .iface import *
from .model import TransportProperties


class ITransportDevice(IAgent):
    """
    搬运设备（智能体的一种），同时具备移动属性
    """

    def is_valid(self) -> bool:
        return True

    @classmethod
    def with_properties(cls, p: TransportProperties, **kwargs):
        inst = cls(**kwargs)
        inst.props = p
        return inst

    props: Optional[TransportProperties] = None

    def load(self, *args, **kwargs):
        """
        装载过程
        """
        t = get_time(self.props.load_distance, self.props.load_speed)
        yield self.env.timeout(t)

    def unload(self, *args, **kwargs):
        """
        卸载过程
        """
        l = self.props.unload_distance or self.props.load_distance
        v = self.props.unload_speed or self.props.load_speed
        t = get_time(l, v)
        yield self.env.timeout(t)

    def move(self, *args, **kwargs):
        """
        移动过程
        """
        d = self.props.distance_vector
        assert d is not None, "coordinates given can't be None"
        yield self.env.timeout(get_time_3d(d, self.props.speed))
        self.props.current_location = copy.copy(self.props.target_location)

    def find_path(self, *args, **kwargs):
        """
        寻找路径
        """
        raise NotImplementedError("find_path method not implemented")


class ObstacleDetectorConfig(BaseModel):
    """
    障碍检测配置
    """

    agent_as_obstacle: bool = False
    rack_as_obstacle: bool = False
    end_point_as_obstacle: bool = False


class ObstacleDetectorOutput(BaseModel):

    obstacles: List[Point] = Field(default_factory=list)

    model_config = DEFAULT_PYDANTIC_MODEL_CONFIG


@runtime_checkable
class ObstacleDetector(Protocol):
    """
    障碍检测器
    """

    def detect_obstacles(
        self, config: Optional[ObstacleDetectorConfig] = None, *args, **kwargs
    ) -> ObstacleDetectorOutput:
        pass


class ManagedMovable(metaclass=ABCMeta):
    """
    按照外部manager规划路线进行移动
    FIXME: 此方式暂未完全实现
    """

    SIGNAL_RESTORE = "restore"

    @abstractmethod
    def get_target_location(self) -> Point:
        pass

    @abstractmethod
    def get_current_location(self) -> Point:
        pass

    @abstractmethod
    def _managed_move_(
        self, end: Point, start: Optional[Point] = None, **kwargs
    ) -> Generator:
        pass

    def __init__(self, *args, **kwargs):
        self.__control_queue__ = Queue()
        self.routine: Queue[Point] = Queue()
        self.__state__: Optional[Literal["paused", "stopped", "active"]] = None

        self.__last_routine__: List[Point] = []
        self.__lock__ = Lock()

    def clear_routine(self):
        """
        清除阻塞队列中的所有点
        """
        with self.__lock__:
            logging.debug("clear routine, before size is %s", self.routine.qsize())
            return self.routine.queue.clear()

    def update_routine(self, routine: Iterable[Point]):
        """
        更新阻塞队列中的路线:删除原有点并添加新的点
        """
        routine = list(routine)
        logging.debug("%s -> %s", self.__last_routine__, routine)
        self.clear_routine()
        for point in routine:
            self.routine.put(point)
        self.__last_routine__ = list(routine)

    def stop_moving_by_routine(self):
        """
        停止移动
        """
        self.__state__ = "stopped"
        logging.debug("%s is stopped", self)

    def pause_moving_by_routine(self):
        self.__state__ = "paused"
        logging.debug("%s is paused", self)
        self.__control_queue__.queue.clear()

    def restore_moving_by_routine(self):
        """
        恢复暂停的进度
        """
        if not self.is_paused:
            logging.warning("%s is not paused, can't restore", self)
            return
        self.__state__ = "active"
        self.__control_queue__.put(self.SIGNAL_RESTORE)
        logging.debug("%s is restored", self)

    def is_routine_empty(self) -> bool:
        return self.routine.empty()

    def wait_routine_empty(self, interval: float = 1):
        """
        等待移动完成
        """
        while not self.is_routine_empty():
            logging.debug(
                "%s is waiting for routine is empty, now size is %s",
                self.__class__.__name__,
                self.routine.qsize(),
            )
            yield from self.wait(interval)

    @abstractmethod
    def wait(self, time: float = 0):
        pass

    @abstractmethod
    def process(self, generator: Generator):
        pass

    @property
    def is_paused(self) -> bool:
        return self.__state__ == "paused"

    @property
    def is_stopped(self) -> bool:
        return self.__state__ == "stopped"

    @property
    def is_active(self) -> bool:
        return self.__state__ == "active"

    def _get_next_point(self, **kwargs) -> Point:
        """
        获取下一个点
        """
        if self.is_paused:
            return self.__control_queue__.get(**kwargs)
        return self.routine.get(**kwargs)

    def start_moving_by_routine(
        self,
        until_target: bool = False,
        until_empty: bool = False,
        wait_interval: float = 3,
        **kwargs,
    ):
        """
        按照阻塞队列中的路线移动
        """
        assert self.is_active is not True, "already moving by routine"
        logging.debug("%s start moving by routine", self)

        self.__state__ = "active"
        # TODO: 加锁?
        # 调用此方法即是强制开启移动，是否正在移动中由调用方判断
        last_point = None
        # 在运行过程中外部调用可能停止此过程
        while not (self.is_stopped):
            if until_empty and self.routine.empty():
                logging.debug("%s routine is empty, will stop", self)
                break
            try:
                next_point = self._get_next_point()
                if next_point == self.SIGNAL_RESTORE:
                    continue
            except:
                logging.debug("%s is waiting for next point", self)
                yield from self.wait(wait_interval)
                continue
            if self.is_stopped:
                break
            logging.debug(
                "%s last is %s,current is %s,next is %s",
                self,
                last_point,
                self.get_current_location(),
                next_point,
            )
            if last_point is not None and last_point != self.get_current_location():
                logging.warning(
                    "%s!=%s,who update current_location?",
                    last_point,
                    self.get_current_location(),
                )
            yield self.process(self._managed_move_(end=next_point, **kwargs))
            if (
                until_target
                and self.get_current_location() == self.get_target_location()
            ):
                break
            last_point = next_point

        self.stop_moving_by_routine()
        logging.info("%s stop moving by routine", self)


class AutonomousMovable(metaclass=ABCMeta):
    """
    自主移动
    """
