# This is a work in progress and is not ready for use


Design:

* Uses Django Storage API
* Uses flexible meta data store


Usage

settings.py::

    THUMBNAILS = {
        'METADATA': {
            'BACKEND': 'thumbnails.backends.metadata.DatabaseBackend',
        },
        'STORAGE': {
            'BACKEND': 'django.core.files.storage.FileSystemStorage',
        }
        'SIZES': {
            'small': {
                'processors': [
                    {'processor': 'thumbnails.processors.resize', 'width': 10, 'height': 10},
                    {'processor': 'thumbnails.processors.crop', 'width': 80, 'height': 80}
                ],
            },
            'default': {
                'processors':[
                    {'processor': 'thumbnails.processors.resize', 'width': 80, 'height': 80},
                    {'processor': 'thumbnails.processors.rotate', 'degrees': 45},
                ]
            },
            'large': {
                'processors': [
                    {'processor': 'thumbnails.processors.resize', 'width': 20, 'height': 20},
                    {'processor': 'thumbnails.processors.flip', 'direction': 'horizontal'}
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
    food.image.thumbnails.create('default')
    food.image.thumbnails.default.url



Builtin processors::

    # To use the following processors, put the arguments of processors in SIZES definition
    thumbnails.processors.resize(width, height)
    thumbnails.processors.rotate(degrees)
    thumbnails.processors.flip(direction)
    thumbnails.processors.crop(width, height, center)

    Processors will be applied to the image sequentially with the order of definition


Running tests::

    `which django-admin.py` test thumbnails --settings=thumbnails.tests.settings --pythonpath=.
