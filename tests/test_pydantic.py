import re

import pytest
from pydantic import AliasChoices, BaseModel, ConfigDict, Field, ValidationError

from logis.event import T


class TestModel(BaseModel):
    name: str | None = Field(validation_alias=AliasChoices("名称"))
    age: int | None = Field(validation_alias=AliasChoices("年龄", "age"))

    model_config = ConfigDict(extra="ignore")


def test_validation_alias_choices():
    form = dict(名称="张三", age="18", not_exist=True)
    m = TestModel.model_validate(form)
    assert m.name == "张三"
    assert m.age == 18

    form = dict(name="张三", 年龄="18")
    m = TestModel.model_validate(form, by_alias=True, by_name=True)
    assert m.name == "张三"
    assert m.age == 18

    with pytest.raises(ValidationError):
        form = dict(name="张三", 年龄="18")
        m = TestModel.model_validate(form, by_alias=True)
        assert m.name == "张三"
        assert m.age == 18
