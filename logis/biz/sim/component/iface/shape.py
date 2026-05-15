from logis.biz.sim.iface import IBlueprint
from logis.biz.sim.storage import IStorage
from logis.iface import Shape


class IShapeBlueprint(IBlueprint, Shape, IStorage):
    """
    形状蓝图组件的抽象基类,例如点节点、举行节点
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def pre_store(self, *args, **kwargs):
        """目前没有容量限制无需预存"""
        pass

    def pre_retrieve(self, *args, **kwargs):
        """目前没有容量限制无需预取"""
        pass
