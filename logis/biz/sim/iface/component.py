import logging
from abc import ABC
from typing import (
    TYPE_CHECKING,
    Iterable,
    Optional,
    Protocol,
    Self,
    Type,
    Union,
    runtime_checkable,
)

from logis.biz.sim.const import ComponentType
from logis.data_type.unitable import Length
from logis.simpy import ISimLock

from ..data_type import ComponentConfigItem, Point
from .location import Locatable

if TYPE_CHECKING:
    from logis.biz.sim.component import ComponentForm


class IComponent(Locatable, ISimLock):
    """
    类型标识
    历史逻辑区分蓝图和空间标记两种概念，为了统一衍生出此接口
    但后续在改造的过程中，逐步把空间标记也视为蓝图，此接口作为更抽象的接口存在
    """

    TYPE: ComponentType = ComponentType.NoneType
    """
    组件类型枚举值, 默认值为NoneType
    """

    def __init__(self, entity: Optional["ComponentForm"] = None, **kwargs):
        super().__init__(**kwargs)
        self.__entity_data__ = entity
        attrs = entity.properties if entity else {}
        self.name: Optional[str] = attrs.get("名称") or kwargs.get("name", None)
        """蓝图实例的名称"""
        self.create_edit_id: Union[str, None] = (
            entity.create_edit_id if entity else None
        )
        """蓝图实例的ID,这个字段命名是历史原因，暂时保留，后续统一为id？"""
        self.type_id: Optional[str] = (entity.type_id if entity else None) or attrs.get(
            "type_id", self.TYPE.id_str()
        )
        """蓝图的类型ID"""
        self.type_name: Optional[str] = (
            entity.type_name if entity else None
        ) or attrs.get("type_name", self.TYPE.label())
        """蓝图的类型名称"""
        self.show_name: Optional[str] = attrs.get("显示名称")

        if (entity or attrs) and (not self.type_id):
            logging.warning(f"{self.__class__}({self.name})未在初始化阶段解析到类型ID")

        self.__center_point__: Optional[Point] = Point.try_parse(attrs)
        """中心点"""
        self.current_jobs: int = 0
        """当前作业数"""

    def increase_jobs(self, *args, **kwargs):
        """
        增加作业数
        """
        self.current_jobs += 1

    def decrease_jobs(self, *args, **kwargs):
        """
        减少作业数
        """
        self.current_jobs -= 1
        if self.current_jobs < 0:
            logging.warning(
                "%s(%s)作业数低于0，当前为%s",
                self.__class__.__name__,
                self.create_edit_id,
                self.current_jobs,
            )

    def on_scene_parsed(self, **kwargs):
        """
        场景解析完成时调用

        之所以有这个方法，是因为有些组件的属性依赖于其他组件初始化完成，但组件初始化的顺序不可控，
        这里索性支持在所有组件初始化完成后调用此放啊补全

        Args:
            kwargs: 其他参数
        """
        pass

    @property
    def center_point(self) -> Optional[Point]:
        """
        获取中心点
        """
        return self.__center_point__

    @center_point.setter
    def center_point(self, value: Optional[Point]):
        """
        设置中心点
        """
        self.__center_point__ = value

    def distance_to(self, target: Self, **kwargs) -> Union[Length, None]:
        """
        默认实现是：计算源点和目标点的中心距离
        """
        if self.center_point is None:
            return None
        return self.center_point.distance_to(target.center_point)

    def is_valid(self):
        """
        判断组件是否有效
        """
        return True

    def previous_nodes(self, direct: bool = True, **kwargs) -> Iterable[Self]:
        """
        获取上游节点

        Args:
            direct (bool, optional): 是否只获取直接上游节点。默认值为True。
        """
        raise NotImplementedError("previous_nodes method not implemented")

    def next_nodes(self, direct: bool = True, **kwargs) -> Iterable[Self]:
        """
        获取下游节点

        Args:
            direct (bool, optional): 是否只获取直接下游节点。默认值为True。
        """
        raise NotImplementedError("next_nodes method not implemented")


@runtime_checkable
class ComponentLoader(Protocol):
    """
    组件加载器、解析器
    """

    def load(self, item: ComponentConfigItem) -> Type[IComponent]:
        """
        加载组件

        Args:
            item (ComponentConfigItem): 组件配置项

        Returns:
            Type[IComponent]: 组件类
        """
        raise NotImplementedError("load method not implemented")
