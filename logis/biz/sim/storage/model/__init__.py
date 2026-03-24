import logging
from collections import defaultdict
from typing import Dict, List, Literal, Optional, Set, Type, Union, get_args, get_origin

from pydantic import AliasChoices, Field, ValidationInfo, field_validator

from logis.biz.sim.const import RackType
from logis.biz.sim.stock import QuantifiedStock
from logis.data_type import (
    DEFAULT_PYDANTIC_MODEL_CONFIG,
    Capacity,
    QuantifiedValue,
    SpatialProps,
    Time,
)


class ContainerMetadata(SpatialProps):
    """
    容器元数据
    """

    model_config = DEFAULT_PYDANTIC_MODEL_CONFIG
    id: Optional[str] = Field(
        validation_alias=AliasChoices("id", "平堆区编号", "货架编号", "储位编码"),
        default=None,
    )

    name: Optional[str] = Field(
        validation_alias=AliasChoices("名称", "name"), default=None
    )

    capacity: Optional[Capacity] = None
    occupied_capacity: Optional[Capacity] = None

    @field_validator("width", "height", "depth", mode="before")
    def check_width(cls: Type[QuantifiedValue], v, validation_info: ValidationInfo):
        """
        其实这里为了避免重复逻辑，就要通过反射来获取字段的类型，麻烦了点但是也长了见识
        """
        field = cls.model_fields.get(validation_info.field_name)
        # field_type = get_origin(field.annotation)
        field_types = get_args(field.annotation)
        field_types: List[Type[QuantifiedValue]] = list(
            filter(lambda t: issubclass(t, QuantifiedValue), field_types)
        )
        if isinstance(v, str) and field_types:
            v = field_types[0].parse_str(v)
        return v

    @field_validator("rotation", mode="before")
    def check_rotation(cls, v, validation_info: ValidationInfo):
        if not v:
            return None
        try:
            return QuantifiedValue(quantity=float(v), unit=None)
        except Exception as e:
            logging.warning("convert failed：%s", e)
        return None

    @property
    def free_capacity(self) -> Capacity:
        return (
            self.capacity - self.occupied_capacity
            if self.occupied_capacity
            else self.capacity
        )

    disabled: Optional[bool] = False

    store_speed_time: Optional[Time] = None
    # 如果不指定默认使用store_speed_time
    retrieve_speed_time: Optional[Time] = None

    # # 是否是互斥访问
    # exclusive: bool = True

    # 内部可以放置的物品类型
    allowed_stock_type: Optional[Union[str, List[str]]] = None

    @property
    def allowed_stock_types(self):
        """
        这里为了方便访问，返回一个固定格式的列表
        """
        if isinstance(self.allowed_stock_type, str):
            return [self.allowed_stock_type]
        elif isinstance(self.allowed_stock_type, list):
            return self.allowed_stock_type
        return ["*"]

    def get_cells(self) -> List["CellProperties"]:
        """
        获取所有的储位
        """
        if hasattr(self, "cells"):
            return self.cells
        return [self]

    def group_cell_by_stock_type(self) -> Dict[str, List["CellProperties"]]:
        dc = defaultdict(list)
        for cell in self.get_cells():
            for allowed_type in cell.allowed_stock_types:
                items = dc[allowed_type]
                items.append(cell)
                dc[allowed_type] = items
        return dc

    def is_allowed_stock_type(self, stock_type: str) -> bool:
        tps = self.allowed_stock_types
        return "*" in tps or stock_type in tps

    def can_store(self, v: QuantifiedStock) -> bool:
        """
        判断当前存储单元是否可以存储指定货物
        1. 类型符合
        2. 空间足够
        """
        return self.is_allowed_stock_type(v.unique_id) and self.free_capacity >= v

    def can_retrieve(self, v: QuantifiedStock) -> bool:
        """
        判断当前存储单元是否可以提供指定货物
        1. 类型符合
        2. 空间足够
        3. 未被占用
        """
        if self.occupied_capacity is None:
            return False
        return self.is_allowed_stock_type(v.unique_id) and self.occupied_capacity >= v


class CellProperties(ContainerMetadata):
    """
    储位属性
    """

    model_config = DEFAULT_PYDANTIC_MODEL_CONFIG

    # # 储位编码
    # cell_id: Optional[str] = None
    # 货架编码
    rack_id: Optional[str] = None
    # 货架组编码
    rack_group_id: Optional[str] = None

    # 储位存储的货物信息
    stocks: List["QuantifiedStock"] = []

    def store(self, v: QuantifiedStock) -> bool:
        """
        存储货物
        """
        ok = self.can_store(v)
        if ok:
            self.stocks.append(v)
        return ok

    def retrieve(self, v: QuantifiedStock) -> bool:
        """
        取出货物
        """
        ok = self.can_retrieve(v)
        if ok:
            self.stocks.remove(v)
        return ok


class RackProperties(ContainerMetadata):
    """
    货架的属性信息
    """

    rack_group_id: Optional[str] = None

    type: Optional[RackType] = Field(
        None, validation_alias=AliasChoices("类型", "type")
    )
    # TODO: 考虑去除
    is_obstacle: Optional[bool] = Field(
        validation_alias=AliasChoices("是否障碍", "is_obstacle", "是障碍"), default=None
    )

    row_count: int = Field(
        validation_alias=AliasChoices("层数", "row_count"), default=1
    )
    col_count: Optional[int] = Field(
        validation_alias=AliasChoices("单元格数", "列数", "col_count"), default=None
    )

    cell_metadata: Optional[ContainerMetadata] = None

    cell_ids: List[str] = Field(default_factory=list)
    cells: List[CellProperties] = Field(default_factory=list)


class RackGroupProperties(ContainerMetadata):
    """
    货架组
    """

    model_config = DEFAULT_PYDANTIC_MODEL_CONFIG

    rack_ids: List[str] = Field(default_factory=list)
    racks: List[RackProperties] = Field(default_factory=list)


class AsrsProperties(RackProperties):
    """
    立库属性信息
    """

    type: Literal["一货架，一堆垛机", "两货架，一堆垛机"] = Field(alias="立库系统类型")


StorageProperties = Union[RackGroupProperties, RackProperties, CellProperties]
