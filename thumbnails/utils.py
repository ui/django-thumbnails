import os
from django.utils import importlib


def import_attribute(name):
    """
    Return an attribute from a dotted path name (e.g. "path.to.func").
    Copied from nvie's rq https://github.com/nvie/rq/blob/master/rq/utils.py
    """
    module_name, attribute = name.rsplit('.', 1)
    module = importlib.import_module(module_name)
    return getattr(module, attribute)


def generate_filename(source_name, size):
    name, extension = os.path.splitext(source_name)
    return "%s_%s%s" % (name, size, extension)
