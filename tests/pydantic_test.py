from abc import ABCMeta

import pytest
from pydantic import AliasChoices, BaseModel, ConfigDict, Field

MODEL_CONFIG = ConfigDict(
    arbitrary_types_allowed=True, validate_by_alias=True, validate_by_name=True
)


class NumberUnit(metaclass=ABCMeta):
    unit: str | None = None
    quantity: int | float = 1

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class QuantifiedValue(NumberUnit, BaseModel):

    def __init__(cls, *args, **kwargs):
        super().__init__(*args, **kwargs)

    model_config = MODEL_CONFIG
    name: str | None = None


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


class ComplexClass:

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name: str = "hello"


def test_mro():
    import inspect

    class Combined2(QuantifiedValue, ComplexClass):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)

    class Combined(ComplexClass, QuantifiedValue):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            # QuantifiedValue.__init__(self, **kwargs)
            # ComplexClass.__init__(self, **kwargs)

    from logis.util.visual_util import draw_mro_tree

    draw_mro_tree(Combined, Combined2)

    c = Combined()
    assert c.name == "hello"

    with pytest.raises(AssertionError):
        c2 = Combined2()
        assert c2.name == "hello"
