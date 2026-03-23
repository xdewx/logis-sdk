from typing import TypeVar

from logis.biz.sim.storage import IStorage


class IRack(IStorage):
    """
    货架
    """

    pass


RackClass = TypeVar("RackClass", bound=IRack)


class IRackGroup(IStorage):
    """
    货架组
    """

    pass


RackGroupClass = TypeVar("RackGroupClass", bound=IRackGroup)
