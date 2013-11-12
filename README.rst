Design
- Uses Django Storage API
- Uses flexible meta data store


Metadata store API:
- storage.add_source(name)
- storage.delete_source(name)
- storage.get_thumbnails(source_name)
- storage.get_thumbnail(source_name, size)
- storage.add_thumbnail(source_name, size)
- storage.delete_thumbnail(source_name, size)




Usage

settings.py:

```
THUMBNAILS = {
    'META_STORAGE_BACKEND': 'thumbnails.backends.metadata.DatabaseBackend',
    'FILE_STORAGE_BACKEND': 'django.core.files.storage.FileSystemStorage'
    'SIZES': {
        'small': {
            'width': 10,
            'height': 10,
        },
        'default': {
            'width': 20,
            'height': 20,
        },
        'large': {
            'width': 30,
            'height': 30,
        }
    }
}
```


```
import thumbnails

class Food(models.Model):
    image = thumbnails.Field()


food = Food.objects.latest('id')
food.image.thumbnails['default'].url
```

Running Tests

```
`which django-admin.py` test thumbnails --settings=thumbnails.tests.settings --pythonpath=.
```