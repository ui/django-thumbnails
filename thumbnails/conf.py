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
POST_PROCESSORS = THUMBNAILS.get('POST_PROCESSORS', [])


# import the processors as a functions and replace the import string
for size in SIZES:
    SIZES[size]['processors'] = parse_processors(SIZES[size]['processors'])


if not isinstance(POST_PROCESSORS, (list, tuple)):
    raise ValueError('POST_PROCESSORS must be in list format')


POST_PROCESSORS = parse_processors(POST_PROCESSORS)
