from django.conf import settings

from .utils import import_attribute

THUMBNAILS = getattr(settings, 'THUMBNAILS', {})

METADATA_BACKEND = THUMBNAILS.get('METADATA_BACKEND', 'thumbnails.backends.metadata.DatabaseBackend')
STORAGE_BACKEND = THUMBNAILS.get('STORAGE_BACKEND', 'django.core.files.storage.FileSystemStorage')
SIZES = THUMBNAILS.get('SIZES', {})

# import the processors as a functions and replace the import string
for size in SIZES:
    processors = SIZES[size].get('processors', [])
    if not isinstance(processors, (list, tuple)):
        raise ValueError('%s processors must be in list format' % size)
    if processors:
        SIZES[size]['processors'] = [import_attribute(processor) for processor in processors]
