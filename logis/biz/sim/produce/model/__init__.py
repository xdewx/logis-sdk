from numbers import Number
from typing import Any, Dict, List, Optional, Union

from pydantic import AliasChoices, BaseModel, Field

from logis.biz.sim.stock import QuantifiedStock
from logis.data_type import (
    DEFAULT_PYDANTIC_MODEL_CONFIG,
    QuantifiedValue,
    Time,
)


class RecipeItemVo(QuantifiedStock):
    model_config = DEFAULT_PYDANTIC_MODEL_CONFIG

    name: str = Field(validation_alias=AliasChoices("FreightType", "name"))
    quantity: Union[int, Number] = Field(
        validation_alias=AliasChoices("FreightCount", "quantity"), default=1
    )
    unit: str = Field(validation_alias=AliasChoices("FreightUnit", "unit"))

    current_location: Any = None
    target_location: Any = None

    @property
    def unique_id(self):
        return f"{self.name}"

    def __str__(self):
        return f"{self.name}({self.quantity}{self.unit})"


Material = RecipeItemVo
Product = RecipeItemVo


class Recipe(BaseModel):
    """
    配方：描述什么材料生成什么产品，多对多关系，应作为最小单元使用
    """

    model_config = DEFAULT_PYDANTIC_MODEL_CONFIG

    materials: List[RecipeItemVo]
    products: List[RecipeItemVo]

    # 耗时
    cycle_time: Time

    def material_dict(self):
        dc: dict[str, QuantifiedValue] = dict()
        for m in self.materials:
            k = m.unique_id
            dc[k] = m
        return dc

    def product_dict(self):
        dc: Dict[str, RecipeItemVo] = dict()
        for p in self.products:
            k = p.unique_id
            dc[k] = p
        return dc

    def io_dict(self):
        """
        获取材料和产品的映射关系
        """
        return dict(**self.material_dict(), **self.product_dict())

    def get_unit(self, name: str):
        return self.io_dict().get(name).unit


class ProduceProperties(BaseModel):
    """
    生产设备属性
    """

    model_config = DEFAULT_PYDANTIC_MODEL_CONFIG

    name: Optional[str] = Field(validation_alias=AliasChoices("名称"))

    # 基本配方
    recipe: Optional[Recipe] = None
    # 原料
    materials: List[Material] = []
    # 产出
    products: List[Product] = []
    # 有时候可能只需要知道数量
    product_quantity: Optional[Number] = None
