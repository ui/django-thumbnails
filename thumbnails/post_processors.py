import imghdr
import os
from subprocess import call, PIPE
import tempfile


def process(thumbnail_file, **kwargs):
    """
    Post processors are functions that receive file objects,
    performs necessary operations and the results as file objects.

    TODO: This method will leave processed files on /tmp,
          we need to figure out the cleanup method
    TODO: Possible race condition on writing to the same file
    """
    temp_dir = tempfile.gettempdir()
    workdir = os.path.join(temp_dir, 'workfile')
    thumbnails = os.path.join(workdir, 'thumbnails')
    if not os.path.exists(workdir):
        os.mkdir(workdir)

    # Write to thumbnails file
    f = open(thumbnails, 'wb')
    f.write(thumbnail_file.read())
    f.close()

    #Optimize image
    optimized_path = optimize_image(thumbnails)
    return open(optimized_path, 'r')


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
        commands.append(u"jpegoptim -f --strip-all '%(file)s'")
    elif filetype == "png":
        #commands.append(u"optipng -force -o7 '%(file)s'")
        commands.append(
            (u"pngcrush -rem gAMA -rem alla -rem cHRM -rem iCCP -rem sRGB "
             u"-rem time '%(file)s' '%(file)s.diet' "
             u"&& mv '%(file)s.diet' '%(file)s'")
        )

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
