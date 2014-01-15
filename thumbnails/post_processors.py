import imghdr
import os
from subprocess import call, PIPE
import tempfile
import uuid

from django.core.files import File


def get_or_create_temporary_folder():
    temp_dir = tempfile.gettempdir()
    workdir = os.path.join(temp_dir, 'workfile')
    if not os.path.exists(workdir):
        os.mkdir(workdir)
    return workdir


def process(thumbnail_file, **kwargs):
    """
    Post processors are functions that receive file objects,
    performs necessary operations and the results as file objects.
    """
    workdir = get_or_create_temporary_folder()
    random_file_name = 'thumbnails%s' % uuid.uuid4().hex
    thumbnails = os.path.join(workdir, random_file_name)

    f = open(thumbnails, 'wb')
    f.write(thumbnail_file.read())
    f.close()

    optimized_path = optimize_image(thumbnails)
    optimized_file = File(open(optimized_path, 'r'))

    os.remove(optimized_path)
    return optimized_file


def optimize_image(thumbnail_path):
    """
    Method to optimize image using tools that are available.
    Logic is taken from image-diet https://github.com/samastur/image-diet/blob/master/image_diet/diet.py
    """

    # Detect filetype
    filetype = imghdr.what(thumbnail_path)

    # Construct command to optimize image based on filetype
    commands = []
    if filetype == "jpeg":
        commands.append("jpegoptim -f --strip-all '%(file)s'")
    elif filetype == "png":
        commands.append("optipng -force -o7 '%(file)s'")
        #commands.append(
            #("pngcrush -rem gAMA -rem alla -rem cHRM -rem iCCP -rem sRGB "
             #u"-rem time '%(file)s' '%(file)s.diet' "
             #u"&& mv '%(file)s.diet' '%(file)s'")
        #)

    # Run Command
    if commands:
        command = " && ".join(commands) % {'file': thumbnail_path}
        try:
            status_code = call(command, shell=True, stdout=PIPE)
        except:
            raise ValueError('Cannot optimize image with parameters %s', command)
        if status_code != 0:
            # Failed.
            raise ValueError('Cannot optimize image. Missing utilities')
    return thumbnail_path
