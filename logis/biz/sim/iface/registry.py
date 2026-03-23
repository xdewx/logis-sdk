from logis.iface import IRegistry

from .blueprint import IBlueprint


class IBlueprintRegistry(IRegistry[IBlueprint]):
    """
    蓝图注册中心
    """
