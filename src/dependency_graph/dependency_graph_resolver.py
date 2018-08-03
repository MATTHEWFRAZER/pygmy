from framework_primivites.dependency_primitives.dependency_with_mutable_dependencies import DependencyWithMutableDependencies
from framework_primivites.primitive_marker import MarionettePrimitive


class DependencyGraphResolver(object):
    RESOLVED_DEPENDENCY_GRAPH = {}

    @classmethod
    def resolve_dependency_graph(cls, dependency_graph, scope_key_string):
        dependency_graph_copy = {key : DependencyWithMutableDependencies(value) for key, value in dependency_graph.items()}
        while dependency_graph_copy:
            dependency_obj = cls.get_node_with_no_out_edges(dependency_graph_copy)
            dependency_obj_name = dependency_obj.dependency_name
            cls.pop_all_references_to_dependency(dependency_graph_copy, dependency_obj_name)
            graph_node = cls.get_graph_node_from_dependency_object(dependency_obj, scope_key_string)
            cls.RESOLVED_DEPENDENCY_GRAPH[dependency_obj_name] = graph_node

    @classmethod
    def get_graph_node_from_dependency_object(cls, dependency_obj, scope_key_string):
        return cls.apply_dependencies(dependency_obj, scope_key_string) if cls.is_resolvable_dependency(dependency_obj) else dependency_obj

    @classmethod
    def is_resolvable_dependency(cls, dependency_obj):
        return all(not cls.is_dependency_obj(dependency_name) for dependency_name in dependency_obj.dependencies)

    @classmethod
    def is_dependency_obj(cls, dependency_name):
        obj = cls.RESOLVED_DEPENDENCY_GRAPH[dependency_name]
        obj_type = type(obj)
        return obj_type.__name__ == "Dependency" and issubclass(obj_type, MarionettePrimitive) and not obj.treat_as_resolved_obj

    @classmethod
    def apply_dependencies(cls, dependency_obj, scope_key_string):
        resolved_dependencies = [cls.RESOLVED_DEPENDENCY_GRAPH[dependency] for dependency in dependency_obj.dependencies]
        return dependency_obj.locate(scope_key_string, *resolved_dependencies)

    @staticmethod
    def pop_all_references_to_dependency(dependency_graph, dependency_name):
        dependency_graph.pop(dependency_name)
        for dependency_obj in dependency_graph.values():
            dependency_obj.mutable_dependencies = [dependency for dependency in dependency_obj.mutable_dependencies if
                                                   dependency != dependency_name]

    @staticmethod
    def get_node_with_no_out_edges(dependency_graph):
        for dependency in dependency_graph.values():
            if not dependency.mutable_dependencies:
                return dependency
        else:
            raise BaseException("dependency_primitives graph has some unresolvable dependencies")