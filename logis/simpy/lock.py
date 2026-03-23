from abc import ABC, abstractmethod

import simpy
import simpy.resources.resource
from ipa.decorator import deprecated


class ISimLock(ABC):

    @property
    @abstractmethod
    def env(self) -> simpy.Environment:
        pass

    def __init__(self, **kwargs):
        self._occupied_ = simpy.Resource(self.env, capacity=1)

    @property
    @deprecated("use is_locked instead")
    def is_occupied(self):
        """
        判断锁是否被占用
        """
        return self.is_locked

    @property
    def is_locked(self):
        return self._occupied_.count > 0

    def lock(self):
        """
        请求锁
        """
        return self._occupied_.request()

    def unlock(self, req: simpy.resources.resource.Request):
        """
        请求解锁
        """
        return self._occupied_.release(req)
