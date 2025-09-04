__doc__ = "工具类"


from typing import Any


def none_if_in(some_value: Any, *choices: Any):
    """
    如果值在choices中，返回None，否则返回原值
    """
    return None if some_value in choices else some_value
