from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

THUMBNAILS = getattr(settings, 'THUMBNAILS', {})

METADATA_BACKEND = THUMBNAILS.get('METADATA_BACKEND', None)
STORAGE_BACKEND = THUMBNAILS.get('STORAGE_BACKEND', None)
SIZES = THUMBNAILS.get('SIZES', None)


def get_size(size):
    if not SIZES:
        raise ImproperlyConfigured("Cannot find THUMBNAIL SIZES in settings.")

    size_dict = SIZES.get(size, None)
    if not size_dict:
        raise ImproperlyConfigured("Cannot find %s in settings." % size)
    return size_dict
