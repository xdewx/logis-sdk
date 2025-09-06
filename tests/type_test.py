from logis.data_type import Number
from logis.data_type.unitable import (
    Capacity,
    Length,
    NumberUnit,
    QuantifiedValue,
    Speed,
    SpeedVector,
    merge_quantified_value,
)


def test_number():
    assert isinstance(10, Number)
    assert isinstance(1.1, Number)


def test_capacity():
    x = Capacity.parse_tuple([10, "箱"])
    assert isinstance(x, Capacity)
    x = Capacity.parse_tuple([10, "箱"])
    assert isinstance(x, Capacity)
    assert isinstance(x, NumberUnit)
    assert isinstance(x, QuantifiedValue)


def test_speed():
    x = Speed.parse_str("1|m/s")
    assert isinstance(x, Speed)
    assert x.quantity == 1
    assert x.unit == "m/s"

    y: SpeedVector = []

    assert type(y) is list
    # 这里没办法判断是SpeedVector类型
    assert type(y) is not SpeedVector


def test_length():
    x = Length(quantity=2, unit="cm")
    y = Length.parse_str("10|cm")

    z1 = x + y
    assert z1.quantity == 12
    z2 = x - y
    assert z2.quantity == -8
    print(z1, z2)


def test_merge_value():
    x = Length.parse_tuple([10, "m"])
    y = Length.parse_tuple([2.1, "cm"])
    z = Length.parse_tuple([20, "cm"])
    try:
        merge_quantified_value([x, y])
    except Exception as e:
        print(e)

    a = merge_quantified_value([x, y, z])
    assert a.quantity == 10.221
    assert a.unit == "m"

    a = merge_quantified_value([x, y, z], target_unit="cm")
    assert a.quantity == 1022.1
    assert a.unit == "cm"


def test_compare():

    a = QuantifiedValue(quantity=10)
    b = Capacity(quantity=11)
    assert a < b
    assert b > a


def test_parse():
    v = QuantifiedValue.model_validate({"quantity": 10, "unit": "m"})
    assert v.quantity == 10
    assert v.unit == "m"
