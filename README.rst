Design:
* Uses Django Storage API
* Uses flexible meta data store


Usage

settings.py::

    THUMBNAILS = {
        'METADATA_BACKEND': 'thumbnails.backends.metadata.DatabaseBackend',
        'STORAGE_BACKEND': 'django.core.files.storage.FileSystemStorage',
        'SIZES': {
            'small': {
                'width': 10,
                'height': 10,
            },
            'default': {
                'width': 20,
                'height': 20,
                'processor': 'thumbnails.processors.resize',
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



Running tests::

    `which django-admin.py` test thumbnails --settings=thumbnails.tests.settings --pythonpath=.
