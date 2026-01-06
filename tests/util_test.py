from logis.util import cast_if_not_none, round_if_not_none, set_attr_if, set_attr_if_has
from logis.util.dict_util import remove_key_not_in
from logis.util.num_util import split_integer


def test_round_if_not_none():
    assert round(3.745, 2) == 3.75
    assert round(3.74512, 2) == 3.75
    assert round(1216.745, 2) == 1216.74
    assert round(1216.74512, 2) == 1216.75

    assert round_if_not_none(1216.745, 2) == 1216.75
    assert round_if_not_none(1216.74512, 2) == 1216.75
    assert round_if_not_none(3.745, 2) == 3.75
    assert round_if_not_none(3.74512, 2) == 3.75

    assert round_if_not_none(3.74512, None) == 3.74512
    assert round_if_not_none(None, 2) is None
    assert round_if_not_none(None, None) is None


def test_cast_if_not_none():
    assert cast_if_not_none(3.14159, int) == 3
    assert cast_if_not_none(3.14159, float) == 3.14159
    assert cast_if_not_none(None, int) is None
    assert cast_if_not_none(None, float) is None


def test_split_integer():
    assert list(split_integer(10, 3, order="asc", mode="limit_parts")) == [3, 3, 4]
    assert list(split_integer(10, 3, order="desc", mode="limit_parts")) == [4, 3, 3]

    assert list(split_integer(10, 3, order="desc", mode="limit_per_part")) == [
        3,
        3,
        3,
        1,
    ]
    assert list(split_integer(10, 3, order="asc", mode="limit_per_part")) == [
        1,
        3,
        3,
        3,
    ]


def test_remove_key_not_in():
    dc = dict(a=1, b=2, c=3, d=4)
    remove_key_not_in(dc, dict(d=5, e=6).keys())
    assert list(dc.keys()) == ["d"]


class Animal:
    def __init__(self):
        self.name = None
        self.age = None


def test_set_attr_if():

    a = Animal()
    set_attr_if_has(
        a,
        dict(name="dog", age=10, gender=1),
    )

    assert a.name == "dog"
    assert a.age == 10
    assert getattr(a, "gender", None) is None

    set_attr_if(a, dict(gender=1), lambda *args: True)

    assert hasattr(a, "gender") and getattr(a, "gender") == 1
