import imghdr
import os
from subprocess import call, PIPE
import tempfile
import uuid

from django.core.files import File


def get_or_create_temp_dir():
    temp_dir = os.path.join(tempfile.gettempdir(), 'thumbnails')
    if not os.path.exists(temp_dir):
        os.mkdir(temp_dir)
    return temp_dir


def process(thumbnail_file, **kwargs):
    """
    Post processors are functions that receive file objects,
    performs necessary operations and return the results as file objects.
    """
    from . import conf

    for post_processor in conf.POST_PROCESSORS:
        post_processor['processor'](thumbnail_file, **post_processor['kwargs'])

    return thumbnail_file


def optimize(thumbnail_file, **kwargs):
    """
    Method to optimize image using tools that are specified in settings.
    Logic is taken from samastur's image_diet
    https://github.com/samastur/image-diet/blob/master/image_diet/diet.py
    """
    temp_dir = get_or_create_temp_dir()
    thumbnail_filename = os.path.join(temp_dir, "%s" % uuid.uuid4().hex)

    f = open(thumbnail_filename, 'wb')
    f.write(thumbnail_file.read())
    f.close()

    # Detect filetype
    filetype = imghdr.what(thumbnail_filename)

    # Construct command to optimize image based on filetype
    command = None
    if filetype == "jpg" or filetype == "jpeg":
        command = kwargs.pop('jpg_optimize_command')
    elif filetype == "png":
        command = kwargs.pop('png_optimize_command')
    elif filetype == "gif":
        command = kwargs.pop('gif_optimize_command')

    # Run Command
    if command:
        command = command % {'filename': thumbnail_filename}
        call(command, shell=True, stdout=PIPE)

    optimized_file = File(open(thumbnail_filename, 'rb'))
    # _get_size() is needed to prevent Django < 1.5 from throwing an AttributeError.
    # This is fixed in https://github.com/django/django/commit/5c954136eaef3d98d532368deec4c19cf892f664
    # and can be removed when we stop supporting Django 1.4
    optimized_file._get_size()

    os.remove(thumbnail_filename)

    return optimized_file
