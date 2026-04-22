__doc__ = """
仿真模块
"""


def test():
    """
    测试函数
    """
    print("This is a test function in the sim module.")


from .data_type import *
from .iface import *
from .storage import ICell, IRack, IRackGroup

Location: TypeAlias = Union[ICell, IRack, IRackGroup, IShapeBlueprint]


class ILocationGetter(IExpose):
    """
    位置获取器接口
    """

    @abstractmethod
    def get(self, **kwargs) -> Optional[Location]:
        """
        获取位置
        """
        pass
