from datetime import datetime
from typing import List, Optional

from ipa.decorator import deprecated
from sqlmodel import Field, Index, Relationship, SQLModel, UniqueConstraint


@deprecated("useless for now")
class StockCellMapping(SQLModel, table=False):
    """
    记录货物储位的映射关系，理论上最小单元的货物和储位是多对一的关系，考虑到扩展的可能，这里使用多对多关系
    """

    __tablename__ = "stock_cell_mapping"
    cell_id: Optional[int] = Field(
        foreign_key="cell.id", primary_key=True, default=None
    )
    stock_id: Optional[int] = Field(
        foreign_key="stock.id", primary_key=True, default=None
    )


@deprecated("useless for now")
class Stock(SQLModel, table=False):
    """
    货物信息
    """

    __tablename__ = "stock"

    id: Optional[int] = Field(
        default=None, primary_key=True, sa_column_kwargs={"autoincrement": True}
    )
    sim_id: str
    # 局部唯一或全局唯一ID
    stock_id: str
    name: str
    quantity: Optional[int] = Field(default=None)
    unit: Optional[str] = Field(default=None)
    sim_now: Optional[int] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    # cell_id适用于多对一关系，这里用多对多关系
    cell_id: Optional[str] = None
    # cells适用于多对多关系
    cells: List["Cell"] = Relationship(
        back_populates="stocks", link_model=StockCellMapping
    )

    __table_args__ = (
        # 联合唯一约束
        UniqueConstraint("sim_id", "stock_id"),
        Index("simid_name", "sim_id", "name"),
    )

    def __repr__(self) -> str:
        return f"Stock(id={self.id}, sim_id={self.sim_id}, stock_id={self.stock_id}, name={self.name}, quantity={self.quantity}, unit={self.unit}, sim_now={self.sim_now},  cell_id={self.cell_id})"


@deprecated("useless for now")
class Cell(SQLModel, table=False):
    """
    记录储位信息
    """

    __tablename__ = "cell"

    id: Optional[int] = Field(
        primary_key=True, sa_column_kwargs={"autoincrement": True}, default=None
    )
    sim_id: str
    cell_id: str
    row: Optional[int] = None
    col: Optional[int] = None
    name: Optional[str] = Field(index=True, default=None)
    # id中可能包含rack_id，此时此字段也不必要
    rack_id: str = Field(default="")
    # 虽然多对一关系可以节省空间，但是维护的关系也复杂，目前用不到，先不那么做
    # rack: "Rack" = Relationship(back_populates="cells")
    stocks: List[Stock] = Relationship(
        back_populates="cells", link_model=StockCellMapping
    )

    __table_args__ = (
        # 联合唯一约束
        UniqueConstraint("sim_id", "cell_id"),
    )


@deprecated("useless for now")
class Rack(SQLModel, table=False):
    """
    记录货架信息
    """

    __tablename__ = "rack"

    id: Optional[int] = Field(
        primary_key=True, sa_column_kwargs={"autoincrement": True}, default=None
    )
    sim_id: str = Field(index=True)
    rack_id: str
    name: str = Field(index=True)
    type: Optional[str] = None
    row_count: Optional[int] = None
    col_count: Optional[int] = None

    # cells: List[Cell] = Relationship(back_populates="rack", cascade_delete=True)

    __table_args__ = (
        # 联合唯一约束
        UniqueConstraint("sim_id", "rack_id"),
    )
