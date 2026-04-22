import logging
from collections import Counter
from typing import Any, Dict, Generic, List, Optional, TypeVar

from pydantic import BaseModel, Field
from toolz import unique

from logis.biz.sim.stock import IStock
from logis.data_type import DEFAULT_PYDANTIC_MODEL_CONFIG, ComponentId
from logis.task import ITask, TaskId

T = TypeVar("T", bound=ITask)


class TaskManifest(BaseModel, Generic[T]):
    """
    任务清单
    """

    model_config = DEFAULT_PYDANTIC_MODEL_CONFIG

    component_id: Optional[ComponentId] = None
    """任务清单所属的组件/蓝图ID"""

    order_tasks: Dict[TaskId, T] = Field(default_factory=dict)
    """订单任务队列"""

    stock_tasks: List[IStock] = Field(default_factory=list)
    """获取任务队列"""

    target_stock_counter: Dict[Any, float] = Field(default_factory=Counter)
    """
    目标货物计数器
        1. key为(货物名称,单位)
        2. value为货物数量
    """
    stock_counter: Dict[Any, float] = Field(default_factory=Counter)
    """
    当前货物计数器
        1. key为(货物名称,单位)
        2. value为货物数量
    """

    def get_task(self, task_id: TaskId) -> Optional[T]:
        """
        根据任务ID获取任务
        """
        return self.order_tasks.get(task_id, None)

    def add_stock_task(self, *stocks: IStock):
        """
        添加货物到货物队列中
        """
        if not stocks:
            return
        self.stock_tasks.extend(stocks)

    def remove_stock_task(self, *stocks: IStock):
        """
        从货物队列中移除货物
        """
        if not stocks:
            return
        for stock in stocks:
            if not stock:
                continue
            if stock in self.stock_tasks:
                self.stock_tasks.remove(stock)
            else:
                logging.error(f"库存{stock}不在清单中")

    @property
    def task_ids(self) -> List[TaskId]:
        """
        获取所有任务ID
        """
        return unique([*self.order_tasks.keys()])

    def add_order_task(self, *order_tasks: T):
        """
        通过判断任务ID是否已存在来判断是否为新任务

        Returns:
            List[OrderTask]: 新添加的订单任务列表
        """
        new_tasks: List[T] = []
        for order_task in order_tasks:
            if not order_task:
                continue
            if order_task.get_task_id() in self.order_tasks:
                continue
            new_tasks.append(order_task)
            self.order_tasks[order_task.get_task_id()] = order_task
        return new_tasks

    def increase_stock_counter(self, stock: "IStock"):
        """
        增加当前货物计数器中的数量
        """
        key = (stock.name, stock.unit)
        self.stock_counter[key] += stock.quantity

    def increase_target_stock_counter(self, stock: "IStock"):
        """
        增加目标货物计数器中的数量
        """
        key = (stock.name, stock.unit)
        self.target_stock_counter[key] += stock.quantity

    def is_stock_io_balanced(self) -> bool:
        """
        通过比较当前货物计数器是否==目标货物计数器，来判断出入货物是否平衡
        """
        return self.stock_counter == self.target_stock_counter

    def is_finished(self) -> bool:
        """
        通过比较当前货物计数器是否>=目标货物计数器，来判断任务是否完成
        """
        return self.stock_counter >= self.target_stock_counter

    def no_stock_task_left(self) -> bool:
        """
        任务队列是否为空
        """
        return not self.stock_tasks
