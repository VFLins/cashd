import importlib
import toga


def get_probe(*args: str):
    relative_path = list(args)
    obj = relative_path.pop()
    full_path = ".".join([f".cashd.probes.{toga.backend}"] + relative_path)
    module = importlib.import_module(full_path, package="tests")
    return getattr(module, obj)
