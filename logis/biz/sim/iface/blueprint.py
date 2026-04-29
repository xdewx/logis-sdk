from abc import abstractmethod
from typing import TYPE_CHECKING, List, Optional, Type, TypeVar

from logis.biz.sim.task.model import TaskManifest
from logis.iface import IControl
from logis.task import ITaskHandler

from ..data_type.component import BlueprintKind
from .component import IComponent
from .proxy import ISimProxy

if TYPE_CHECKING:
    from logis.biz.sim.graph import ISimPathGraph
    from logis.biz.sim.order import IOrder
    from logis.biz.sim.task.model import IStock

class IBlueprint(ISimProxy, ITaskHandler, IComponent, IControl):
    """
    所有蓝图组件的抽象基类
    """

    @abstractmethod
    def get_task_manifest[T](self) -> Optional[TaskManifest[T]]:
        """
        获取任务清单
        """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name: Optional[str] = None
        """蓝图实例的名称"""
        self.create_edit_id: Optional[str] = None
        """蓝图实例的ID"""
        self.type_id: Optional[str] = None
        """蓝图的类型ID"""
        self.type_name: Optional[str] = None
        """蓝图的类型名称"""

    @classmethod
    def verbose_name(cls, *args, **kwargs):
        """
        蓝图的详细名称
        """
        return cls.__name__

    @staticmethod
    @abstractmethod
    def kinds(*args, **kwargs) -> List[BlueprintKind]:
        """
        获取蓝图的种类，之所以有这个，是因为历史逻辑依靠此标志来分组
        """
        pass

    def is_kind_of(self, kind: BlueprintKind) -> bool:
        """
        判断是否是某种蓝图
        """
        return kind in (self.kinds() or [])

    def handle(
        self,
        try_interval: float = 10,
        max_concurrency: int = 10,
        task_manifest: Optional[TaskManifest] = None,
        **taskkwargs,
    ):
        """
        循环处理任务队列中的任务直到队列为空
        1. 任务之间是串行还是并行由max_concurrency决定
        2. 任务执行结束后异步触发on_task_succeeded

        Args:
            try_interval (float, optional): 尝试处理任务的时间间隔，单位秒。默认值为10。
            max_concurrency (int, optional): 最大并发处理任务数量。默认值为10。
            task_manifest (TaskManifest, optional): 任务清单。如果不传则使用实例的任务清单。
        """
        raise NotImplementedError("ITaskHandler.handle尚未实现")

    def handle_stock_task(
        self, stock: "IStock", order: Optional["IOrder"] = None, **kwargs
    ):
        """
        处理单个货物任务

        默认情况下，此方法会在handle方法中作为处理单元被循环调用
        """
        raise NotImplementedError("handle_stock_task 未实现")

    def build_graph(self, graph: "ISimPathGraph"):
        """
        构建蓝图的图结构

        此方法会在各蓝图初始化时被调用，用于构建全局的路径图。

        Args:
            graph (ISimPathGraph): 路径、布局连接图
        """

BlueprintClass = TypeVar("BlueprintClass", bound=IBlueprint)
"""
蓝图类类型
"""

C = TypeVar("C")


class ICodeBlueprint(IBlueprint):
    """
    代码蓝图组件的抽象基类
    """

    def instantiate_strategy(
        self, strategy_type: Type[C], index: int = -1, **kwargs
    ) -> Optional[C]:
        """
        实例化策略

        Args:
            strategy_type (Type[C]): 策略的父类
            index (int, optional): 策略的索引。默认值为-1。
            kwargs (dict): 其他参数

        Returns:
            Optional[C]: 策略实例，如果成功实例化策略，否则返回None

        Raises:
            NotImplementedError: 如果不支持实例化策略
        """
        raise NotImplementedError("instantiate_strategy 未实现")


from logis.iface import Shape


class IShapeBlueprint(IBlueprint, Shape):
    """
    形状蓝图组件的抽象基类,例如点节点、举行节点
    """
