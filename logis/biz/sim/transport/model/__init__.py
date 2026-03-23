from typing import Any, Optional, Protocol, Tuple, Union

from pydantic import BaseModel

from logis.data_type import (
    DEFAULT_PYDANTIC_MODEL_CONFIG,
    Capacity,
    Length,
    Point,
    Speed,
    SpeedVector,
    ThreeDimensionalVelocity,
    Time,
    get_time,
)


class TransportProperties(BaseModel):
    """
    搬运相关属性
    """

    # 单次最大搬运量
    single_max_capacity: Optional[Capacity] = None

    # 起始位置
    start_location: Optional[Point] = None
    # 当前位置
    current_location: Optional[Point] = None
    # 终点位置
    target_location: Optional[Point] = None

    @property
    def distance_vector(self) -> Optional[Point]:
        """
        获取设备位置到终点位置的向量
        """
        start = self.current_location
        end = self.target_location
        if start is None or end is None:
            return None
        return end - start

    # 移动速度
    speed: Union[Speed, ThreeDimensionalVelocity, None] = None

    # 装载速度
    load_speed: Optional[Speed] = None
    # 卸载速度,如果未指定，就使用装载速度
    unload_speed: Optional[Speed] = None

    # 装载距离
    load_distance: Optional[Length] = None
    # 卸载距离，如果未指定，使用装载距离
    unload_distance: Optional[Length] = None

    # 装载时间
    load_time: Optional[Time] = None
    # 卸载时间
    unload_time: Optional[Time] = None

    payload: Any = None

    model_config = DEFAULT_PYDANTIC_MODEL_CONFIG

    @property
    def x_speed(self):
        return self.speed.x

    @property
    def y_speed(self):
        return self.speed.y

    @property
    def z_speed(self):
        return self.speed.z

    def get_load_time(self) -> Time:
        """
        获取装载时间
        """
        return (
            self.load_time
            if self.load_time
            else get_time(self.load_distance, self.load_speed)
        )

    def get_unload_time(self) -> Time:
        """
        获取卸载时间
        """
        return (
            self.unload_time
            if self.unload_time
            else get_time(self.unload_distance, self.unload_speed)
        )


class StackerProperties(TransportProperties):
    """
    堆垛机属性
    """

    # 横向长度
    width: Optional[Length] = None

    # 纵向高度
    height: Optional[Length] = None

    # 总容量
    capacity: Optional[Capacity] = None

    # 已用容量
    used_capacity: Optional[Capacity] = None
