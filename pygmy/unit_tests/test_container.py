import types

from six import with_metaclass
import pytest

from pygmy.scope_binding.scope_enum import ScopeEnum

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
        wired = container.wire_dependencies(Dummy(1, 2, 3).method, "function")
        assert "abcbcc" == wired

    def test_dependencies_can_be_delivered_to_class_method(self, container):
        wired = container.wire_dependencies(Dummy(1, 2, 3).class_method)
        assert "abcbcc" == wired

    def test_partial_wire_up_dependencies_works_when_dependencies_to_ignore_is_empty(self, obj_to_wire_up, container):
        wired = container.partial_wire_dependencies(obj_to_wire_up.dependency_obj)
        assert "xabcbcc" == wired()

    # make sure that exceptions bubble up
    def test_wire_up_dependencies_with_obj_that_is_in_dependency_graph(self, obj_to_wire_up, container):
        try:
            wired = container.wire_dependencies(obj_to_wire_up.dependency_obj)
        except Exception as ex:
            pytest.fail("exception occurred while wiring dependencies: {}".format(ex))

        assert "xabcbcc" == wired

    def test_wire_up_dependencies_with_multiple_connected_components(self, obj_to_wire_up, obj_to_wire_up2, container2):
        wired_up = container2.wire_dependencies(obj_to_wire_up.dependency_obj)
        wired_up2 = container2.wire_dependencies(obj_to_wire_up2.dependency_obj)
        assert wired_up == "xabcbcc"
        assert wired_up2 == "def"

    def test_wire_up_dependencies_with_class_obj(self, container):
        wired_up_dummy = container.wire_dependencies(Dummy)
        assert "abcbcc" == wired_up_dummy.message

    def test_wire_up_dependencies_with_instance_callable(self, container):
        wired_up_call = container.wire_dependencies(Dummy("a", "b", "c"))
        assert wired_up_call == "abcbcc"

    @pytest.mark.xfail(raises=BaseException)
    def test_wire_up_dependencies_with_missing_dependencies(self, container_constructor):
        def a(b): pass
        container_constructor.wire_dependencies(a)

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

    def test_wire_up_dependencies_with_dynamically_generated_methods(self, container, dependency_decorator):
        @dependency_decorator(global_dependency=True)
        def inner_a(): return "a"

        class A(object): pass

        a = A()
        # using non standard wa
        a.non_valid_method = lambda inner_a: inner_a
        # eventually don't use self as a first argument (e.g. _) as one might
        a.method = types.MethodType(lambda self, inner_a: inner_a, a)

        assert "a" == container.wire_dependencies(a.non_valid_method) == container.wire_dependencies(a.method)

    @pytest.mark.skip(reason="not supported")
    def test_wire_up_dependencies_with_class_introspection_generated_method(self, container, dependency_decorator):
        @dependency_decorator(global_dependency=True)
        def inner_a(): return "a"

        class A(object): pass

        setattr(A, "method", lambda inner_a: inner_a)
        # eventually don't use cls as first argument (e.g use _ as one might)
        setattr(A, "classmethod", classmethod(lambda cls, inner_a: inner_a))
        setattr(A, "staticmethod", staticmethod(lambda inner_a: inner_a))

        assert "a" == container.wire_dependencies(A.method) == container.wire_dependencies(A.staticmethod) == container.wire_dependencies(A.classmethod)

    def test_partial_wire_up_dependencies_gets_correct_value_with_instance_scope_when_later_call_to_wire_up(self, dependency_decorator, container):
        @dependency_decorator(scope=ScopeEnum.CLASS, global_dependency=True)
        def conflict(): return WireUp()

        class WireUp:
            def method(self, conflict):
                return conflict

        partially_wired = container.partial_wire_dependencies(WireUp().method)
        assert container.wire_dependencies(WireUp().method) is partially_wired()

    def test_wire_up_dependencies_with_instance_introspection_generated_method(self, container_constructor):
        # test two instances that generate the same methods, class scope should get the same, instance and below should not
        pass
    def test_wire_up_dependencies_with_metaclass_generated_methods(self, container, dependency_decorator):
        @dependency_decorator(global_dependency=True)
        def meta_test():
            return meta_test.__name__

        class MetaClass(type):
            def __new__(mcs, name, bases, attributes):
                class_instance = type(name, bases, attributes)
                setattr(class_instance, "method", lambda self, meta_test: meta_test)
                return class_instance

        class A(with_metaclass(MetaClass)): pass

        assert container.wire_dependencies(A().method) == meta_test.__name__


    def test_wire_up_dependencies_to_staticmethod_from_getattr(self, container, dependency_decorator):
        @dependency_decorator(global_dependency=True)
        def staticmethod_getattr_test():
            return staticmethod_getattr_test.__name__

        class A(object):
            @staticmethod
            def s(staticmethod_getattr_test): return staticmethod_getattr_test

        assert container.wire_dependencies(getattr(A, "s")) == staticmethod_getattr_test.__name__

    def test_wire_up_dependencies_to_classmethod_from_getattr(self, container, dependency_decorator):
        @dependency_decorator(global_dependency=True)
        def classmethod_getattr_test():
            return classmethod_getattr_test.__name__

        class A(object):
            @classmethod
            def c(cls, classmethod_getattr_test): return classmethod_getattr_test

        assert container.wire_dependencies(getattr(A, "c")) == classmethod_getattr_test.__name__

    def test_wire_up_dependencies_to_instance_method_from_getattr(self, container, dependency_decorator):
        @dependency_decorator(global_dependency=True)
        def instance_method_getattr_test():
            return instance_method_getattr_test.__name__

        class A(object):
            def i(self, instance_method_getattr_test): return instance_method_getattr_test

        assert container.wire_dependencies(getattr(A(), "i")) == instance_method_getattr_test.__name__

    def test_wire_up_dependencies_to_dereferenced_classmethod(self, container, dependency_decorator):
        @dependency_decorator(global_dependency=True)
        def classmethod_test():
            return classmethod_test.__name__

        class A(object):
            @classmethod
            def c(cls, classmethod_test): return classmethod_test

        assert container.wire_dependencies(A.c) == classmethod_test.__name__

    def test_wire_up_dependencies_to_staticmethod(self, container, dependency_decorator):
        @dependency_decorator(global_dependency=True)
        def static_dereference_test():
            return static_dereference_test.__name__

        class A(object):
            @staticmethod
            def s(static_dereference_test): return static_dereference_test

        assert container.wire_dependencies(A.s) == static_dereference_test.__name__

    @pytest.mark.skip(reason="will fail because the class reference will not be resolved to dereferenced function")
    def test_wire_up_dependencies_to_dereferenced_classmethod(self, container, dependency_decorator):
        @dependency_decorator(global_dependency=True)
        def dereferenced_test():
            return dereferenced_test.__name__

        class A(object):
            @classmethod
            def c(cls, dereferenced_test):
                return dereferenced_test

        assert container.wire_dependencies(A.__dict__["c"].__func__) == dereferenced_test.__name__

    def test_wire_up_dependencies_to_dereferenced_staticmethod(self, container, dependency_decorator):
        @dependency_decorator(global_dependency=True)
        def dereferenced_test():
            return dereferenced_test.__name__

        class A(object):
            @staticmethod
            def s(dereferenced_test):
                return dereferenced_test

        assert container.wire_dependencies(A.__dict__["s"].__func__) == dereferenced_test.__name__