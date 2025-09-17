__doc__ = "工具类"


from typing import Any, Callable, Optional


def first_not_none[T](*args: T) -> Optional[T]:
    for item in args:
        if item is not None:
            return item
    return None


def none_if_in(some_value: Any, *choices: Any):
    """
    如果值在choices中，返回None，否则返回原值
    """
    return None if some_value in choices else some_value


def set_attr_if(obj: Any, props: dict, cond: Callable[[str, Any], bool]):
    """
    如果指定对象满足条件则设置目标属性的值
    """
    assert obj is not None, "obj can't be None"
    for k, v in props.items():
        if cond(k, v):
            setattr(obj, k, v)


def set_attr_if_has(obj: Any, props: dict):
    """
    如果目标对象存在指定属性则设置
    """
    set_attr_if(obj, props, lambda k, v: hasattr(obj, k))
