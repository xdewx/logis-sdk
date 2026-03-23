from abc import ABC

import simpy
import simpy.resources.resource


class ISimLock(ABC):

    def __init__(self, env: simpy.Environment):
        self._occupied_ = simpy.Resource(env, capacity=1)
        self._lock_ = False

    @property
    def is_occupied(self):
        """
        判断锁是否被占用
        """
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
