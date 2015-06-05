from copy import deepcopy

try:
    import importlib
except ImportError:
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


def parse_processors(processor_definition):
    """
    Returns a dictionary that contains the imported processors and
    kwargs. For example, passing in:

    processors = [
        {'processor': 'thumbnails.processors.resize', 'width': 10, 'height': 10},
        {'processor': 'thumbnails.processors.crop', 'width': 10, 'height': 10},
    ]

    Would return:

    [
        {'processor': resize_function, kwargs: {'width': 10, 'height': 10}}
        {'processor': crop_function, kwargs: {'width': 10, 'height': 10}}
    ]
    """
    parsed_processors = []
    for processor in processor_definition:
        processor_function = import_attribute(processor['PATH'])
        kwargs = deepcopy(processor)
        kwargs.pop('PATH')
        parsed_processors.append({
            'processor': processor_function,
            'kwargs': kwargs
        })

    return parsed_processors
