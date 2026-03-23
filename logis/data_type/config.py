from pathlib import Path
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


class AppConfig(BaseModel):
    """
    应用常用配置
    """

    app_name: str
    root_dir: Optional[Path] = None
    runtime_root_dir: Optional[Path] = None
    data_dir: Optional[Path] = None
    logs_dir: Optional[Path] = None
    sidecar_dir: Optional[Path] = None
    conf_dir: Optional[Path] = None

    model_config = DEFAULT_PYDANTIC_MODEL_CONFIG
