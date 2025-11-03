from typing import Generic

from pydantic import BaseModel

from .base import DEFAULT_PYDANTIC_MODEL_CONFIG, T


class ApiError(BaseModel):
    code: int = -1
    message: str = "未知错误"


class ApiResponse(BaseModel, Generic[T]):

    success: bool
    data: T | None = None
    error: ApiError | str | None = None
    message: str | None = None
    extra: dict | None = None

    model_config = DEFAULT_PYDANTIC_MODEL_CONFIG

    @staticmethod
    def positive[T](data: T, **kwargs):
        return ApiResponse[T](success=True, data=data, **kwargs)

    @staticmethod
    def negative(error: ApiError | str, **kwargs):
        return ApiResponse[None](success=False, error=error, **kwargs)
