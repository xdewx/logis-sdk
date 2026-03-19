from abc import ABC, ABCMeta, abstractmethod
from typing import Generic, TypeVar

T = TypeVar("T")


class IRegistry(ABC, Generic[T]):

    @abstractmethod
    def register(self, *args, **kwargs):
        pass

    @abstractmethod
    def unregister(self, *args, **kwargs):
        pass

    @abstractmethod
    def get[T](self, *args, **kwargs) -> T:
        pass
