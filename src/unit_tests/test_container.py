import pytest


class Dummy(object):
    def __init__(self, a, b, c):
        self.message = a + b + c
        self.__name__ = "test"

    def __call__(self, a, b, c):
        return a + b + c

    def method(self, a, b, c):
        return a + b + c

    @classmethod
    def class_method(cls, a, b, c):
        return a + b + c


class TestContainer(object):

    def test_dependencies_can_be_delivered_to_bound_method(self, container):
        wired = container.wire_dependencies(Dummy(1, 2, 3).method)
        assert "abcbcc" == wired

    def test_dependencies_can_be_delivered_to_class_method(self, container):
        wired = container.wire_dependencies(Dummy(1, 2, 3).class_method)
        assert "abcbcc" == wired

    def test_partial_wire_up_dependencies_works_when_dependencies_to_ignore_is_empty(self, obj_to_wire_up, container):
        wired = container.partial_wire_dependencies(obj_to_wire_up)
        assert "xabcbcc" == wired()

    # make sure that exceptions bubble up
    def test_wire_up_dependencies_with_obj_that_is_in_dependency_graph(self, obj_to_wire_up, container):
        try:
            wired = container.wire_dependencies(obj_to_wire_up)
        except Exception as ex:
            pytest.fail("exception occurred while wiring dependencies: {}".format(ex))

        assert "xabcbcc" == wired

    @pytest.mark.skip(reason="the logic for checking for a dependency_primitives to have the __name__ attribute does not reside in the container")
    @pytest.mark.xfail(raises=ValueError)
    def test_wire_up_dependencies_with_invalid_obj(self, container):
        container.wire_dependencies("invalid obj")

    def test_wire_up_dependencies_with_multiple_connected_components(self, obj_to_wire_up, obj_to_wire_up2, container2):
        wired_up = container2.wire_dependencies(obj_to_wire_up)
        wired_up2 = container2.wire_dependencies(obj_to_wire_up2)
        assert wired_up == "xabcbcc"
        assert wired_up2 == "def"

    def test_wire_up_dependencies_with_class_obj(self, container):
        wired_up_dummy = container.wire_dependencies(Dummy)
        assert "abcbcc" == wired_up_dummy.message

    def test_wire_up_dependencies_with_instance_callable(self, container):
        wired_up_call = container.wire_dependencies(Dummy("a", "b", "c"))
        assert wired_up_call == "abcbcc"

    def test_wire_up_dependencies_with_missing_dependencies(self, container):
        def a(b): pass
        container.wire_dependencies(a)

    def test_partial_wire_up_dependencies(self, partial_dependency_fixture):

        def expect_specific_types(a, b):
            assert a == "abc"
            assert b == "bc"

        try:
            partially_wired = partial_dependency_fixture.container.partial_wire_dependencies(expect_specific_types, *partial_dependency_fixture.ignored_dependencies)
        except Exception as ex:
            pytest.fail(". Ex {0}".format(ex))
        else:
            partially_wired(*partial_dependency_fixture.left_over_dependencies)

    def test_partial_wire_up_dependencies_to_instance_obj(self, partial_dependency_fixture):
        try:
            partial_wired = partial_dependency_fixture.container.partial_wire_dependencies(Dummy("a", "b", "c").method, *partial_dependency_fixture.ignored_dependencies)
        except Exception as ex:
            pytest.fail(". Ex {0}".format(ex))
        else:
            obj = partial_wired(*partial_dependency_fixture.left_over_dependencies)

        assert obj == "abcbcc"
