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


# import default first
DEFAULT_SIZE = SIZES.pop('default')
DEFAULT_PROCESSORS = None
DEFAULT_POSTPROCESSORS = None

if DEFAULT_SIZE:
    DEFAULT_PROCESSORS = parse_processors(DEFAULT_SIZE['PROCESSORS'])
    DEFAULT_POSTPROCESSORS = parse_processors(DEFAULT_SIZE['POST_PROCESSORS'])


# import the processors as a functions and replace the import string
for size in SIZES:
    if SIZES[size].get('PROCESSORS'):
        SIZES[size]['PROCESSORS'] = parse_processors(SIZES[size]['PROCESSORS'])
    elif DEFAULT_PROCESSORS:
        SIZES[size]['PROCESSORS'] = DEFAULT_PROCESSORS

    if SIZES[size].get('POST_PROCESSORS'):
        SIZES[size]['POST_PROCESSORS'] = parse_processors(SIZES[size]['POST_PROCESSORS'])
    elif DEFAULT_POSTPROCESSORS:
        SIZES[size]['POST_PROCESSORS'] = DEFAULT_POSTPROCESSORS

SIZES['default'] = {}
SIZES['default']['PROCESSORS'] = DEFAULT_PROCESSORS
SIZES['default']['POST_PROCESSORS'] = DEFAULT_POSTPROCESSORS
