__doc__ = """
字典工具类
"""

from typing import Any, Callable, Iterable, Tuple

cn_en_dict = dict(
    半径="radius",
)


def unify_key_name(input: dict, mappings: dict = cn_en_dict) -> dict:
    """
    将字典的键名按照字典中的映射规则进行统一转换
    Args:
        input (dict): 输入的字典，键名可能是中文或其他形式。
        mappings (dict): 键名映射规则，键为原始键名，值为目标键名。
    """
    output = dict()
    for k, v in input.items():
        new_key = mappings.get(k, k)
        if new_key in output:
            raise ValueError(f"Duplicate key found: {new_key} in input dictionary.")
        output[new_key] = v
    return output


def remove_key_not_in(dc: dict, keys: Iterable[Any]):
    """
    移除不在指定范围内的key
    """
    for key in list(dc.keys()):
        if key not in keys:
            dc.pop(key)


def get_the_first_existent_key(obj: dict, *keys) -> Tuple[Any, Any]:
    """
    获取第一个存在的key的值
    """
    for key in keys:
        if key in obj:
            return key, obj[key]
    return None, None
