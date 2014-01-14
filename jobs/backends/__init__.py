from django.core.exceptions import ImproperlyConfigured

try:
    from importlib import import_module
except ImportError:
    from django.utils.importlib import import_module


def get_backend(path):
    i = path.rfind('.')
    module, attr = path[:i], path[i+1:]
    try:
        mod = import_module(module)
    except ImportError, e:
        raise ImproperlyConfigured('Error loading job backend %s: "%s"' % (module, e))
    try:
        backend_class = getattr(mod, attr)
    except AttributeError:
        raise ImproperlyConfigured('Module "%s" does not define a job backend named "%s"' % (module, attr))
    return backend_class


