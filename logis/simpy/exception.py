from simpy.core import StopSimulation


class DeadlineException(StopSimulation):
    """
    截止事件异常
    """

    def __init__(self, cause):
        super().__init__(cause)
