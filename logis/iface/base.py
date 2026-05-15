from abc import ABC


class Interface(ABC):
    """
    为了避免多继承的参数传递问题，这里兜底处理所有多余参数

    使用时全部继承本接口即可
    """

    def __init__(self, *args, **kwargs) -> None:
        super().__init__()
