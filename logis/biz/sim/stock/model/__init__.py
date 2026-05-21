from abc import ABCMeta
from numbers import Number
from typing import TYPE_CHECKING, Literal, Optional, Tuple

from logis.data_type import DEFAULT_PYDANTIC_MODEL_CONFIG, NumberUnit, QuantifiedValue
from logis.task import ITask

if TYPE_CHECKING:
    from logis.biz.sim import LocationLike

class QuantifiedStock(QuantifiedValue):
    """
    基础货物属性
    """

    model_config = DEFAULT_PYDANTIC_MODEL_CONFIG

    sku: Optional[str] = None
    name: str
    code: Optional[str] = None

    # 默认数量为1
    quantity: Number = 1

    order_id: Optional[str] = None
    task_id: Optional[str] = None

    @property
    def unique_id(self):
        return self.sku or self.code or self.name

    @property
    def storage_key(self) -> Tuple[str, str]:
        """
        用于存储索引的key，格式为(name, unit)，
        """
        return (self.name, self.unit)


# TODO: 考虑组合实现和QuantifiedStock同源
class IStock(NumberUnit, metaclass=ABCMeta):
    # class IStock(QuantifiedStock):
    """
    库存\货物接口
    """

    order_id: Optional[str] = None
    task_id: Optional[str] = None

    name: str
    code: Optional[str] = None

    stage: Optional[str] = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__stage__: Optional[Literal["pickup", "delivery"]] = kwargs.get(
            "__stage__"
        )
        """内部状态变量"""

    @property
    def unique_id(self):
        return self.code or self.name

    @property
    def id(self):
        """
        货物的ID
        """
        raise NotImplementedError(f"{self}未实现id属性")

    @property
    def target_location(self) -> "LocationLike":
        raise NotImplementedError()

    @target_location.setter
    def target_location(self, location: "LocationLike"):
        raise NotImplementedError()

    @property
    def current_location(self) -> "LocationLike":
        raise NotImplementedError()

    @current_location.setter
    def current_location(self, location: "LocationLike"):
        raise NotImplementedError()

    @property
    def final_target_location(self) -> "LocationLike":
        """
        起初只有当前位置和目标位置，但是后来发现有些场景下目标位置只是短期目标，短期目标会经常更换
        """
        raise NotImplementedError()

    @final_target_location.setter
    def final_target_location(self, loc: "LocationLike"):
        raise NotImplementedError()

    @property
    def storage_key(self) -> Tuple[str, str]:
        """
        用于存储索引的key，格式为(name, unit)，
        """
        return (self.name, self.unit)

    def set_arrived(self):
        """
        设置货物到达目标位置
        """
        self.current_location = self.target_location


class StockTask(ITask, IStock):
    pass
