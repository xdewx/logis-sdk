from typing import Union

import simpy

from .exception import DeadlineException
from .util import schedule_event_at


class DeadlineEvent(simpy.Event):
    """
    截止事件，用于在指定时间触发**DeadlineException**异常从而正常退出
    如果仿真早于截止时间完成, 则此事件仍会执行
    """

    def interrupt(self, *args, **kwargs):
        """
        中断事件
        """
        # 如果后续还有事件,忽略事件正常退出,此时时钟停止在deadline时间
        raise DeadlineException(f"deadline {self.at} reached, force exit")

    def __init__(
        self,
        env: simpy.Environment,
        at: Union[float, int, None] = None,
    ):
        super().__init__(env)
        self.at: Union[float, int, None] = None
        self._ok = True
        self._value = None
        if at is not None:
            self.schedule_at(at)
        # self.callbacks = [StopSimulation.callback]
        self.callbacks = [self.interrupt]

    def schedule_at(self, at: Union[float, int]):
        """
        计划在指定时间触发事件
        Args:
            at (float | int): 触发时间
        """
        if self.at is not None:
            raise ValueError("deadline event already scheduled")
        self.at = at
        return schedule_event_at(self.env, at, self)
