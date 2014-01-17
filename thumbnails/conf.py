from django.conf import settings

from .utils import import_attribute

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

DEFAULT_PROCESSORS = THUMBNAILS.get('DEFAULT_PROCESSORS', [])
if not isinstance(DEFAULT_PROCESSORS, (list, tuple)):
    raise ValueError('Default processors must be in list format')

# import the processors as a functions and replace the import string
for size in SIZES:
    processors = SIZES[size].get('processors', DEFAULT_PROCESSORS)
    if not isinstance(processors, (list, tuple)):
        raise ValueError('%s processors must be in list format' % size)
    if processors:
        SIZES[size]['processors'] = [import_attribute(processor) for processor in processors]
    else:
        SIZES[size]['processors'] = processors
