from inspect import getargspec

from dependency_graph.dependency_graph_manager import DependencyGraphManager
from framework_primivites.dependency_primitives.dependency import Dependency
from framework_primivites.dependency_primitives.dependency_initialization_methods import DependencyInitializationMethods
from framework_primivites.partial_injection import PartialInjection
from framework_primivites.primitive_marker import MarionettePrimitive


class Container(MarionettePrimitive):

    @classmethod
    def wire_dependencies(cls, obj_to_wire_up, *dependencies_to_ignore, scope_overwrite="function"):
        return cls.partial_wire_dependencies(obj_to_wire_up, *dependencies_to_ignore, scope_overwrite=scope_overwrite)()

    @classmethod
    def partial_wire_dependencies(cls, obj_to_wire_up, *dependencies_to_ignore, scope_overwrite="function"):
        DependencyInitializationMethods.input_validation_for_dependency_obj(obj_to_wire_up)
        dependency_obj = Dependency.get_dependency_from_dependency_obj(obj_to_wire_up, scope_overwrite)
        resolved_dependencies = DependencyGraphManager.resolve_dependencies(dependency_obj, *dependencies_to_ignore)
        resolved_dependency_names = [dependency for dependency in dependency_obj.dependencies if dependency not in dependencies_to_ignore]
        args_to_apply_as_dict = dict(zip(resolved_dependency_names, resolved_dependencies))
        return PartialInjection(obj_to_wire_up, dependencies_to_ignore,**args_to_apply_as_dict)