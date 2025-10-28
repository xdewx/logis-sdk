__doc__ = """
指标模块
"""


from abc import ABC, abstractmethod
from typing import TypeVar

from pydantic import BaseModel


class MetricModel(ABC):
    """
    指标模型
    """

    @abstractmethod
    def get_measurement(self) -> str:
        """
        获取指标名称
        """
        pass


MetricModelType = TypeVar("MetricModelType", bound=MetricModel)
