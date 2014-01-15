import imghdr
import os
from subprocess import call, PIPE
import tempfile
import uuid

from django.core.files import File


def get_or_create_temporary_folder():
    temp_dir = os.path.join(tempfile.gettempdir(), 'thumbnails')
    if not os.path.exists(temp_dir):
        os.mkdir(temp_dir)
    return temp_dir


def process(thumbnail_file, **kwargs):
    """
    Post processors are functions that receive file objects,
    performs necessary operations and the results as file objects.
    """
    from . import conf
    temp_dir = get_or_create_temporary_folder()
    thumbnail_filename = os.path.join(temp_dir, "%s.png" % uuid.uuid4().hex)

    f = open(thumbnail_filename, 'wb')
    f.write(thumbnail_file.read())
    f.close()

    for post_processor in conf.POST_PROCESSORS['processors']:
        post_processor(thumbnail_filename)

    optimized_file = File(open(thumbnail_filename, 'rb'))
    # _get_size() is needed to prevent Django < 1.5 from throwing an AttributeError.
    # This is fixed in https://github.com/django/django/commit/5c954136eaef3d98d532368deec4c19cf892f664
    # and can be removed when we stop supporting Django 1.4
    optimized_file._get_size()

    os.remove(thumbnail_filename)
    return optimized_file


def optimize_image(thumbnail_path):
    """
    Method to optimize image using tools that are available.
    Logic is taken from image-diet https://github.com/samastur/image-diet/blob/master/image_diet/diet.py
    """
    from . import conf
    # Detect filetype
    filetype = imghdr.what(thumbnail_path)

    # Construct command to optimize image based on filetype
    command = conf.POST_PROCESSORS.get("%s_command" % filetype)

    # Run Command
    if command:
        command = command % {'filename': thumbnail_path}
        try:
            status_code = call(command, shell=True, stdout=PIPE)
        except:
            raise ValueError('Cannot optimize image with parameters %s', command)
        if status_code != 0:
            # Failed.
            raise ValueError('Cannot optimize image. Missing utilities')
    return thumbnail_path
