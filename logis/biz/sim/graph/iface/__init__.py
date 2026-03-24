from logis.data_type import Point
from logis.iface.graph import IPathGraph as _IPathGraph

from ..model import DirEdge


class IPathGraph(_IPathGraph[DirEdge, Point]):
    """
    路径关系图
    """

    pass
