from typing import Type


def load_backend(dotted_path: str) -> Type:
    try:
        module_path = dotted_path.split(".")
        class_name = module_path.pop()
        mod = __import__(".".join(module_path), fromlist=[class_name])
        klass = getattr(mod, class_name)
    except AttributeError as exc:
        raise Exception(f"Path not found: {dotted_path}") from exc
    return klass


class ScopeConfiguration:
    def __init__(self, scope, correlation_id):
        self.scope = scope
        self.correlation_id = correlation_id

    def __call__(self):
        self.scope.set_tag("correlation_id", self.correlation_id)
