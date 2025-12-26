from typing import Generic, Optional, TypeVar, Union

from pydantic import BaseModel

from .base import DEFAULT_PYDANTIC_MODEL_CONFIG

V = TypeVar("V")


class ConfigItem(BaseModel, Generic[V]):
    model_config = DEFAULT_PYDANTIC_MODEL_CONFIG

    namespace: str = ""

    label: Union[str, None] = None
    key: str
    value: Optional[V] = None
    value_type: Optional[str] = None
    disabled: bool = False
