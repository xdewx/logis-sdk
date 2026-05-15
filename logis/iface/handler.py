from abc import ABC, ABCMeta, abstractmethod

from .base import Interface


class IHandler(Interface):
    """
    处理接口
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @abstractmethod
    def handle(self, *args, **kwargs):
        """
        处理数据
        """
