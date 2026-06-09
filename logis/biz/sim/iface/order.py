from abc import ABC, abstractmethod
from datetime import datetime
from typing import Union

from logis.task.model import QuantifiedTask


class IOrder(ABC):
    """
    订单接口，表达一个完整的客户订单
    """

    @abstractmethod
    def get_priority(self) -> int:
        """
        订单优先级,数字越小优先级越高
        """
        pass

    def get_wave_id(self) -> Union[str, int, None]:
        """
        波次ID
        """
        return None

    @abstractmethod
    def set_wave_id(self, wave_id: Union[str, int, None]):
        """
        设置波次ID
        """
        pass

    @abstractmethod
    def get_order_time(self) -> datetime:
        """
        订单时间
        """
        pass


class IOrderTask(IOrder, QuantifiedTask):
    """
    订单任务接口，表达一个订单拆分出来的单个任务
    同时继承订单信息（IOrder）和量化任务能力（QuantifiedTask）
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
