from ploceidae.dependency import Dependency
from ploceidae.scope_binding.scope_enum import ScopeEnum
from ploceidae.scope_binding.scope_key import ScopeKey

class TestDependencyLocation:

    def test_function_scope(self):
        dependency_instance = Dependency()
        l = lambda: type("T", (), {})
        dependency_instance(l)
        key = ScopeKey(l)
        assert dependency_instance.locate(key) != dependency_instance.locate(key)

    def test_non_weak_referenceable_entities_can_be_located(self):
        dependency_instance = Dependency(scope=ScopeEnum.SESSION)
        test = "test"
        l = lambda: test
        dependency_instance(l)
        key = ScopeKey(l)
        key.init_scope(ScopeEnum.SESSION)
        assert dependency_instance.locate(key) == test
        assert test in [item[1] for item in dependency_instance.services.items()]