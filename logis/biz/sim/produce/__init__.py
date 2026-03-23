import logging
import types
from collections import defaultdict
from math import floor
from typing import Any, Generator, List, Optional, Protocol, runtime_checkable

from logis.data_type import merge_quantified_value

from .model import *


@runtime_checkable
class IProduce(Protocol):
    """
    生产设备
    """

    log: logging.Logger

    props: Optional[ProduceProperties] = None

    def can_produce(self, *args, **kwargs) -> bool:
        """
        是否可以生产指定的产品
        """
        raise NotImplementedError()

    def on_material_ready(
        self, materials: List[Material], recipe: Optional[Recipe] = None
    ):
        """
        源材料到达事件回调
        """
        pass

    def on_product_ready(
        self, products: List[Product], recipe: Optional[Recipe] = None
    ):
        """
        产品生产完成事件回调
        """
        raise NotImplementedError()

    def perform_producing(self, *args, **kwargs) -> Generator[Any, Any, List[Product]]:
        """
        真正的生产过程，例如仿真中的timeout过程
        """
        result: List[Product] = []
        raise NotImplementedError()
        return result

    def produce(self, *args, props: Optional[ProduceProperties] = None, **kwargs):
        """
        生产入口
        """
        log = self.log
        p = props or self.props
        materials, recipe = p.materials, p.recipe

        id_recipe_map = recipe.material_dict()
        __id_materials_map = defaultdict(list)
        id_material_map: dict[str, Material] = defaultdict()

        # 把原料合并起来
        for material in materials:
            k = material.unique_id
            __id_materials_map[k].append(material)
        for k, group in __id_materials_map.items():
            id_material_map[k] = merge_quantified_value(group)

        keys = id_recipe_map.keys()

        # 计算现有原料最多能生产多少套产品
        p.product_quantity = count = min(
            [floor(id_material_map[k] / id_recipe_map[k]) for k in keys]
        )

        # 计算剩余原料
        for k, material in id_material_map.items():
            material.decrease(id_recipe_map[k].quantity * count)
        p.materials = list(id_material_map.values())

        # 发出生产完成事件
        for _ in range(count):
            products = yield from self.perform_producing(**kwargs)
            if products:
                r = self.on_product_ready(
                    products=products, recipe=recipe, order=kwargs.get("order")
                )
                if isinstance(r, types.GeneratorType):
                    yield from r
            else:
                log.error("%s produce failed", self)
