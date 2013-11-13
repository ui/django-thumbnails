from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

META_STORAGE_BACKEND = getattr(settings, 'META_STORAGE_BACKEND', None)
FILE_STORAGE_BACKEND = getattr(settings, 'FILE_STORAGE_BACKEND', None)
THUMBNAILS = getattr(settings, 'THUMBNAILS', {})
SIZES = THUMBNAILS.get('SIZES', None)


def get_size(size):
    if not SIZES:
        raise ImproperlyConfigured("Cannot find THUMBNAIL SIZES in settings.")

    size_dict = SIZES.get(size, None)
    if not size_dict:
        raise ImproperlyConfigured("Cannot find %s in settings." % size)
    return size_dict
