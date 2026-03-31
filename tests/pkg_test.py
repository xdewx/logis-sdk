from logis.util.pkg_util import is_subclass_of


def test_is_subclass_of():
    class TestClass:
        pass

    class TestSubclass(TestClass):
        pass

    assert is_subclass_of(TestSubclass, TestClass)
    assert is_subclass_of(TestClass, TestClass)
    assert not is_subclass_of(TestClass, TestClass, include_parent=False)
