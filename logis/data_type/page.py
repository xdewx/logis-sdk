from typing import Generic, TypeVar

from pydantic import AliasChoices, BaseModel, Field

from .base import DEFAULT_PYDANTIC_MODEL_CONFIG

T = TypeVar("T")


class Pager(BaseModel):
    page_base: int | None = Field(
        default=0, validation_alias=AliasChoices("page_base", "pageBase")
    )
    page_size: int = Field(
        default=100, validation_alias=AliasChoices("page_size", "pageSize")
    )
    page_at: int = Field(
        default=0, validation_alias=AliasChoices("page_at", "pageAt", "page")
    )
    total: int | None = None

    model_config = DEFAULT_PYDANTIC_MODEL_CONFIG


class PageResult(Pager, Generic[T]):
    items: list[T]

    model_config = DEFAULT_PYDANTIC_MODEL_CONFIG


class TableQuery(Pager):
    database: str | None = None
    table: str

    model_config = DEFAULT_PYDANTIC_MODEL_CONFIG
