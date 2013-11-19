from django.conf import settings

THUMBNAILS = getattr(settings, 'THUMBNAILS', {})

METADATA_BACKEND = THUMBNAILS.get('METADATA_BACKEND', 'thumbnails.backends.metadata.DatabaseBackend')
STORAGE_BACKEND = THUMBNAILS.get('STORAGE_BACKEND', 'django.core.files.storage.FileSystemStorage')
SIZES = THUMBNAILS.get('SIZES', {})
BASEDIR = THUMBNAILS.get('BASEDIR', 'thumbnails')
