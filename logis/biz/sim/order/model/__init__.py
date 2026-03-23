from datetime import datetime
from typing import Optional, Set

from pydantic import BaseModel, Field

from logis.data_type import DEFAULT_PYDANTIC_MODEL_CONFIG
from logis.task import TaskId


class WaveInfo(BaseModel):
    """
    波次信息
    """

    model_config = DEFAULT_PYDANTIC_MODEL_CONFIG
    wave_start_time: Optional[datetime] = None
    wave_id: Optional[str] = None
    order_ids: Set[str] = Field(default_factory=set)
    task_ids: Set[TaskId] = Field(default_factory=set)
