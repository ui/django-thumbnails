|Build Status|

Design:

* Uses Django Storage API
* Uses flexible meta data store. Database and Redis metadata backend supported at the moment.

Installation
------------

* Add `thumbnails` to `INSTALLED_APPS` in `settings.py`.
* Run `python manage.py migrate` to create database metadata backend.


Usage
-----

settings.py:

.. code-block:: python

    THUMBNAILS = {
        'METADATA': {
            'BACKEND': 'thumbnails.backends.metadata.DatabaseBackend',
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

If you prefer to use Redis as your metadata storage backend (like I do :):

.. code-block:: python

    THUMBNAILS = {
        'METADATA': {
            'PREFIX': 'thumbs',
            'BACKEND': 'thumbnails.backends.metadata.RedisBackend',
            'db': 2,
            'port': 6379,
            'host': 'localhost',
        },
    }


In python:

.. code-block:: python

    import thumbnails

    class Food(models.Model):
        image = thumbnails.Field()


    food = Food.objects.latest('id')
    food.image.thumbnails.all()
    food.image.thumbnails.small  # Generates "small" sized thumbnail
    food.image.thumbnails.large  # Generates "large" sized thumbnail
    food.image.thumbnails.small.url  # Returns "small" sized thumbnail URL 



`django-thumbnails` comes with a few builtin image processors::

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
To run tests::

    `which django-admin.py` test thumbnails --settings=thumbnails.tests.settings --pythonpath=.


=========
Changelog
=========

Version 0.2.0
-------------
* Improves performance on fields that have a large number of thumbnails
* Add support for Django 1.8, 1.9 and 1.10

Version 0.1.3
-------------
* Fixes deprecation warning in Django 1.8

Version 0.1.2
-------------
* Fixes deprecation warning in Django 1.8

Version 0.1.1
-------------
* Use `shortuuid <https://github.com/stochastic-technologies/shortuuid>`_ instead of `uuid4()` to be more space efficient

Version 0.1.0
-------------
* First public release


As of February 2015, this library is suitable for production use and has been used for more than a year in `Stamps <http://stamps.co.id>`_, an Indonesian based CRM/loyalty system.


.. |Build Status| image:: https://travis-ci.org/ui/django-thumbnails.png?branch=master
   :target: https://travis-ci.org/ui/django-thumbnails
