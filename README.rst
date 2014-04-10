# This is a work in progress and is not ready for use

|Build Status|

Design:

* Uses Django Storage API
* Uses flexible meta data store


Usage

settings.py::

    THUMBNAILS = {
        'METADATA': {
            'BACKEND': 'thumbnails.backends.metadata.DatabaseBackend', # Redis backend also supported
        },
        'STORAGE': {
            'BACKEND': 'django.core.files.storage.FileSystemStorage',
            # You can also use Amazon S3 or any other Django storage backends
        }
        'SIZES': {
            'small': {
                'PROCESSORS': [
                    {'PATH': 'thumbnails.processors.resize', 'width': 10, 'height': 10},
                    {'PATH': 'thumbnails.processors.crop', 'width': 80, 'height': 80}
                ],
                'POST_PROCESSORS': [
                    {
                        'processor': 'thumbnails.post_processors.optimize',
                        'png_command': 'optipng -force -o7 "%(filename)s"',
                        'jpg_command': 'jpegoptim -f --strip-all "%(filename)s"',
                    },
                ],
            },
            'large': {
                'PROCESSORS': [
                    {'PATH': 'thumbnails.processors.resize', 'width': 20, 'height': 20},
                    {'PATH': 'thumbnails.processors.flip', 'direction': 'horizontal'}
                ],
            }
        }
    }


In python::

    import thumbnails

    class Food(models.Model):
        image = thumbnails.Field()


    food = Food.objects.latest('id')
    food.image.thumbnails.all()
    food.image.thumbnails.small  # Generates "small" sized thumbnail
    food.image.thumbnails.large  # Generates "large" sized thumbnail
    food.image.thumbnails.small.url  # Returns "small" sized thumbnail URL 



Builtin processors::

    # To use the following processors, put the arguments of processors in SIZES definition
    thumbnails.processors.resize(width, height)
    thumbnails.processors.rotate(degrees)
    thumbnails.processors.flip(direction)
    thumbnails.processors.crop(width, height, center)

    Processors are applied sequentially in the same order of definition.


Management Commands
-------------------
If you changed your size definition and want to regenerate the thumbnails, use::

    python manage.py delete_thumbnails --model=app.Model --size=thumbnail_size_to_delete


Running Tests
-------------

    `which django-admin.py` test thumbnails --settings=thumbnails.tests.settings --pythonpath=.


=========
Changelog
=========

Version 0.1.0
-------------
* First public release


.. |Build Status| image:: https://travis-ci.org/ui/django-thumbnails.png?branch=master
   :target: https://travis-ci.org/ui/django-thumbnails