import logging
import time
from abc import ABC
from typing import Any

import simpy
import simpy.resources
import simpy.resources.resource


def try_put(
    env: simpy.Environment,
    container: simpy.Container,
    amount: int | float,
    timeout: int | None = None,
):
    x = container.put(amount)
    if timeout:
        x = x | env.timeout(0.1)
    v = yield x
    return v


def resize_container(container: simpy.Container, capacity: int | float, is_delta=False):
    capacity = capacity + container.capacity if is_delta else capacity
    container._capacity = capacity
    # return simpy.Container(container._env, capacity, container.level)


def resource_to_dict(resource: Any):
    if isinstance(resource, simpy.Container):
        return dict(level=resource.level, capacity=resource.capacity)
    if isinstance(resource, simpy.Resource):
        return dict(level=resource.count, capacity=resource.capacity)
    if isinstance(resource, simpy.Store):
        return dict(level=len(resource.items), capacity=resource.capacity)
    print("unexpected type:" + resource)


def interrupt_if_timeout(
    env: simpy.Environment,
    timeout: float | None = None,
    check_interval: float = 10,
    exit_signal: simpy.Event | None = None,
):
    """
    根据仿真真实运行时间是否超时来中断仿真

    Args:
        env (simpy.Environment): 仿真环境
        timeout (float | None, optional): 最大运行时间. 默认不限时
        check_interval (float, optional): 这个时间是仿真中的时间
        exit_signal (simpy.Event | None, optional): 外部信号，用于外部中断仿真. 默认不使用.
    """

    def inner():
        if not timeout:
            return
        cpu_start_time = time.time()
        while not (exit_signal and exit_signal.triggered):
            dt = time.time() - cpu_start_time
            if dt > timeout:
                raise simpy.Interrupt(
                    f"仿真运行时间{dt}超过最大运行时间{timeout}，强制退出"
                )
            yield env.timeout(check_interval)
            logging.debug(f"neither timeout nor terninate is received")

    return env.process(inner())


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
