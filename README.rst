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
        },
        'DEFAULT_PROCESSORS': ['thumbnails.processors.resize', '...'],
        'SIZES': {
            'small': {
                'width': 10,
                'height': 10,
            },
            'default': {
                'width': 20,
                'height': 20,
                'processors': ['thumbnails.processors.resize', 'thumbnails.processors.grayscale', 'your.own.processor'],
            },
            'large': {
                'width': 30,
                'height': 30,
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

    If no processors are defined in SIZES definition, django_thumbnails will
    try to find processors defined in default_processors. In this case, arguments
    for the default processor still needs to be defined in respective SIZES definition


Running tests::

    `which django-admin.py` test thumbnails --settings=thumbnails.tests.settings --pythonpath=.
