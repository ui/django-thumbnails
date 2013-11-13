from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

THUMBNAILS = getattr(settings, 'THUMBNAILS', {})

METADATA_BACKEND = THUMBNAILS.get('METADATA_BACKEND', 'thumbnails.backends.metadata.DatabaseBackend')
STORAGE_BACKEND = THUMBNAILS.get('STORAGE_BACKEND', 'django.core.files.storage.FileSystemStorage')
SIZES = THUMBNAILS.get('SIZES', None)


def get_all_sizes():
    if not SIZES:
        raise ImproperlyConfigured("Cannot find THUMBNAIL SIZES in settings.")
    sizes = []
    for size in SIZES:
        sizes.append(size)
    return sizes


def get_size(size):
    if not SIZES:
        raise ImproperlyConfigured("Cannot find THUMBNAIL SIZES in settings.")

    size_dict = SIZES.get(size, None)
    if not size_dict:
        raise ImproperlyConfigured("Cannot find %s in settings." % size)
    return size_dict
