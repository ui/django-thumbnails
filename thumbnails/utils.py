import io

from django.core.files.base import ContentFile
from django.utils import importlib

from da_vinci import images


def import_attribute(name):
    """
    Return an attribute from a dotted path name (e.g. "path.to.func").
    Copied from nvie's rq https://github.com/nvie/rq/blob/master/rq/utils.py
    """
    module_name, attribute = name.rsplit('.', 1)
    module = importlib.import_module(module_name)
    return getattr(module, attribute)


def process_image(file, size):
    """
    Process an image through its defined processors
    return a ContentFile
    """
    from . import conf

    # open image in piccaso
    raw_image = images.from_file(file)

    # run through all processors, if defined
    size_dict = conf.SIZES[size]
    for processor in size_dict.get('processors'):
        raw_image = processor(raw_image, **size_dict)

    # write to Content File
    image_io = io.BytesIO()
    raw_image.save(file=image_io)
    image_file = ContentFile(image_io.getvalue())

    return image_file
