from abc import ABCMeta
from numbers import Number
from typing import Optional

from logis.biz.sim.data_type import LocationType
from logis.data_type import DEFAULT_PYDANTIC_MODEL_CONFIG, NumberUnit, QuantifiedValue
from logis.task import ITask


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

    @property
    def unique_id(self):
        return self.code or self.name

    @property
    def target_location(self) -> LocationType:
        raise NotImplementedError()

    @target_location.setter
    def target_location(self, location: LocationType):
        raise NotImplementedError()

    @property
    def current_location(self) -> LocationType:
        raise NotImplementedError()

    @current_location.setter
    def current_location(self, location: LocationType):
        raise NotImplementedError()

    @property
    def final_target_location(self) -> LocationType:
        """
        起初只有当前位置和目标位置，但是后来发现有些场景下目标位置只是短期目标，短期目标会经常更换
        """
        raise NotImplementedError()

    @final_target_location.setter
    def final_target_location(self, loc: LocationType):
        raise NotImplementedError()


class StockTask(ITask, IStock):
    pass
