from django.utils import importlib


def import_attribute(name):
    """
    Return an attribute from a dotted path name (e.g. "path.to.func").
    Copied from nvie's rq https://github.com/nvie/rq/blob/master/rq/utils.py
    """
    if hasattr(name, '__call__'):
        return name
    module_name, attribute = name.rsplit('.', 1)
    module = importlib.import_module(module_name)
    return getattr(module, attribute)
