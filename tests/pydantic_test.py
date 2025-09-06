from abc import ABCMeta

import pytest
from pydantic import AliasChoices, BaseModel, ConfigDict, Field

MODEL_CONFIG = ConfigDict(
    arbitrary_types_allowed=True, validate_by_alias=True, validate_by_name=True
)


class NumberUnit(metaclass=ABCMeta):
    unit: str | None = None
    quantity: int | float = 1


class QuantifiedValue(BaseModel, NumberUnit):
    model_config = MODEL_CONFIG


class OverideQuantifiedValue(QuantifiedValue):

    unit: str = Field(validation_alias=AliasChoices("xxx", "unit"))

    model_config = MODEL_CONFIG


class Xxx(OverideQuantifiedValue):
    pass


Yyy = OverideQuantifiedValue


def test_override_quantified_value():
    x = OverideQuantifiedValue.model_validate(dict(quantity=10, xxx="m"))
    assert x.quantity == 10
    assert x.unit == "m"

    with pytest.raises(AssertionError):

        x = Xxx.model_validate(dict(quantity=10, xxx="m"))
        assert x.quantity == 10
        assert x.unit == "m"

    y = Yyy.model_validate(dict(quantity=10, xxx="m"))
    assert y.quantity == 10
    assert y.unit == "m"
