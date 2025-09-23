import pytest


class A:
    @property
    def id(self) -> int:
        pass


class B(A):
    def __init__(self):
        self.id = 10


def test_id():
    with pytest.raises(AttributeError):
        b = B()
        assert b.id == 10
