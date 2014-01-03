from thumbnails import conf
from thumbnails.utils import import_attribute


def get_backend():
    backend = import_attribute(conf.STORAGE.get('BACKEND', 'django.core.files.storage.FileSystemStorage'))
    return backend()
