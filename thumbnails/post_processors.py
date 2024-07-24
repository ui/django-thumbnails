from PIL import Image
import os
from subprocess import call
import tempfile
import shortuuid

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
        processor['processor'](thumbnail_file, **processor['kwargs'])

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
                'png_command': 'optipng -force -o3 "%(filename)s"',
                'jpg_command': 'jpegoptim -f --strip-all "%(filename)s"',
            },
        ],
    }

    Note: using output redirection in commands may cause unpredictable results.
    For example 'optipng -force -o3 "%(filename)s" &> /dev/null' may cause
    optimize command to fail on some systems.
    """
    temp_dir = get_or_create_temp_dir()
    thumbnail_filename = os.path.join(temp_dir, "%s" % shortuuid.uuid())

    f = open(thumbnail_filename, 'wb')
    f.write(thumbnail_file.read())
    f.close()

    # Detect filetype
    filetype = Image.open(thumbnail_filename).format.lower()

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
    os.remove(thumbnail_filename)

    return optimized_file
