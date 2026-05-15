import logging
from abc import ABC
from typing import (
    TYPE_CHECKING,
    Iterable,
    Optional,
    Protocol,
    Self,
    Type,
    runtime_checkable,
)

from logis.biz.sim.const import ComponentType
from logis.iface import Interface

from ..data_type import ComponentConfigItem

if TYPE_CHECKING:
    from logis.biz.sim.component import ComponentForm


class IComponent(Interface):
    """
    类型标识
    历史逻辑区分蓝图和空间标记两种概念，为了统一衍生出此接口
    但后续在改造的过程中，逐步把空间标记也视为蓝图，因此此接口似乎就没太多必要，不过作为更抽象的接口，还是保留着
    """

    TYPE: ComponentType = ComponentType.NoneType
    """
    组件类型枚举值
    """

    def __init__(self, entity: Optional["ComponentForm"] = None, **kwargs):
        super().__init__(**kwargs)
        self.__entity_data__ = entity
        attrs = entity.properties if entity else {}
        self.name: Optional[str] = attrs.get("名称") or kwargs.get("name", None)
        """蓝图实例的名称"""
        self.create_edit_id: Optional[str] = entity.create_edit_id if entity else None
        """蓝图实例的ID"""
        self.type_id: Optional[str] = (entity.type_id if entity else None) or attrs.get(
            "type_id", self.TYPE.id_str()
        )
        """蓝图的类型ID"""
        self.type_name: Optional[str] = (
            entity.type_name if entity else None
        ) or attrs.get("type_name", self.TYPE.label())
        """蓝图的类型名称"""
        self.show_name: Optional[str] = attrs.get("显示名称")

        if not self.type_id:
            logging.warning(f"{self}未在初始化阶段解析到类型ID")

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
