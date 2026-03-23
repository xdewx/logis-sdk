from logis.data_type import Point
from logis.math import euclid_distance, manhattan_distance


class DirEdge:
    """
    有向图的连边

    注意：此结构体已废弃，后续统一使用networkx相关
    """

    def __init__(self, starter: Point, ender: Point, speed: float = -1, **kwargs):
        self.starter = starter
        self.ender = ender  ## starter/ender are supposed to be tuple vertices
        # TODO:之前一直用的是欧几里得距离，在仓储场景下，好像曼哈顿距离更合适
        # self.length = manhattan_distance(starter, ender)
        self.length = euclid_distance(starter, ender)
        self.speed = speed

    def __str__(self):
        return f"e({self.starter}-{self.ender})"

    def __repr__(self):
        return str(self)
