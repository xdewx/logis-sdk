from logis.util.num_util import split_integer


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
