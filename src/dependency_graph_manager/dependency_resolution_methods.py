from scope_binding.scope_key import ScopeKey


class DependencyResolutionMethods(object):
    @classmethod
    def resolve_dependencies_by_group(cls, dependency_obj, group):
        dependency_retrieval_method = lambda: [name for name, dependency in cls.DEPENDENCY_GRAPH.items() if dependency.group == group]
        return cls.dependency_resolution_algorithm(dependency_obj, dependency_retrieval_method)

    @classmethod
    def resolve_dependencies_inner(cls, dependency_obj, *dependencies_to_ignore):
        dependency_retrieval_method = lambda: filter(lambda dependency: dependency not in dependencies_to_ignore, dependency_obj.dependencies)
        return cls.dependency_resolution_algorithm(dependency_obj, dependency_retrieval_method)

    @classmethod
    def dependency_resolution_algorithm(cls, dependency_obj, dependency_retrieval_method):
        scope_key = ScopeKey(dependency_obj.dependency_obj)
        with cls.LOCK:
            dependencies = dependency_retrieval_method()
            return cls.resolve_dependencies_as_list(dependencies, scope_key)

    @classmethod
    def resolve_dependencies_as_list(cls, dependencies, scope_key):
        resolved_dependencies = []
        for dependency in dependencies:
            # if there is no need to resolve arguments
            if not cls.DEPENDENCY_GRAPH[dependency].dependencies:
                resolved_dependencies.append(cls.DEPENDENCY_GRAPH[dependency].locate(scope_key))
            else:
                dependency_obj_inner = cls.DEPENDENCY_GRAPH[dependency]
                resolved_args = cls.resolve_dependencies(cls.DEPENDENCY_GRAPH[dependency])
                resolved_dependencies.append(dependency_obj_inner.locate(scope_key, *resolved_args.all_resolved_dependencies))
        return resolved_dependencies