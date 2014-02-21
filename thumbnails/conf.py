from django.conf import settings

from .utils import parse_processors

THUMBNAILS = getattr(settings, 'THUMBNAILS', {})


default_metadata = {
    'BACKEND': 'thumbnails.backends.metadata.DatabaseBackend'
}

default_storage = {
    'BACKEND': 'django.core.files.storage.FileSystemStorage'
}

METADATA = THUMBNAILS.get('METADATA', default_metadata)
STORAGE = THUMBNAILS.get('STORAGE', default_storage)
SIZES = THUMBNAILS.get('SIZES', {})
BASEDIR = THUMBNAILS.get('BASEDIR', 'thumbnails')


# import the processors as a functions and replace the import string
for size in SIZES:
    if SIZES[size].get('PROCESSORS'):
        SIZES[size]['PROCESSORS'] = parse_processors(SIZES[size]['PROCESSORS'])
    else:
        SIZES[size]['PROCESSORS'] = {}

    if SIZES[size].get('POST_PROCESSORS'):
        SIZES[size]['POST_PROCESSORS'] = parse_processors(SIZES[size]['POST_PROCESSORS'])
    else:
        SIZES[size]['POST_PROCESSORS'] = {}
