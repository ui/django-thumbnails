import imghdr
import os
from subprocess import call
import tempfile
import uuid

from django.core.files import File


def get_or_create_temp_dir():
    temp_dir = os.path.join(tempfile.gettempdir(), 'thumbnails')
    if not os.path.exists(temp_dir):
        os.mkdir(temp_dir)
    return temp_dir


def process(thumbnail_file, size, **kwargs):
    """
    Post processors are functions that receive file objects,
    performs necessary operations and return the results as file objects.
    """
    from . import conf

    size_dict = conf.SIZES[size]
    for processor in size_dict['POST_PROCESSORS']:
        processor['PATH'](thumbnail_file, **processor['kwargs'])

    return thumbnail_file


def optimize(thumbnail_file, jpg_command=None, png_command=None,
             gif_command=None):
    """
    A post processing function to optimize file size. Accepts commands
    to optimize JPG, PNG and GIF images as arguments. Example:

    THUMBNAILS = {
        # Other options...
        'POST_PROCESSORS': [
            {
                'processor': 'thumbnails.post_processors.optimize',
                'png_command': 'optipng -force -o7 "%(filename)s"',
                'jpg_command': 'jpegoptim -f --strip-all "%(filename)s"',
            },
        ],
    }

    Note: using output redirection in commands may cause unpredictable results.
    For example 'optipng -force -o7 "%(filename)s" &> /dev/null' may cause
    optimize command to fail on some systems.
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
        command = jpg_command
    elif filetype == "png":
        command = png_command
    elif filetype == "gif":
        command = gif_command

    # Run Command
    if command:
        command = command % {'filename': thumbnail_filename}
        call(command, shell=True)

    optimized_file = File(open(thumbnail_filename, 'rb'))
    # Call _get_size() to prevent Django < 1.5 from throwing an AttributeError.
    # This is fixed in https://github.com/django/django/commit/5c954136eaef3d98d532368deec4c19cf892f664
    # and can be removed when we stop supporting Django 1.4
    optimized_file._get_size()

    os.remove(thumbnail_filename)

    return optimized_file
