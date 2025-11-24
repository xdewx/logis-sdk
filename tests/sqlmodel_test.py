from pydantic import AliasChoices
from sqlmodel import Field, SQLModel

from logis.util.pydantic_util import collect_field_aliases


class TestTableModel(SQLModel, table=False):
    name: str = Field(
        "", alias="名字", schema_extra=dict(validation_alias=AliasChoices("userName"))
    )


def test_collect_alias():
    name_field = TestTableModel.model_fields["name"]
    aliases = collect_field_aliases(name_field)

    assert not aliases.difference(["名字", "userName"])
