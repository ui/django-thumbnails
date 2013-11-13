# -*- coding: utf-8 -*-


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
    },
}


INSTALLED_APPS = (
    'thumbnails',
    'thumbnails.tests',
)

SECRET_KEY = 'a'

THUMBNAILS = {
    'METADATA_BACKEND': 'thumbnails.backends.metadata.DatabaseBackend',
    'STORAGE_BACKEND': 'django.core.files.storage.FileSystemStorage',
    'SIZES': {
        'small': {
            'width': 10,
            'height': 10,
        },
        'default': {
            'width': 20,
            'height': 20,
        },
        'large': {
            'width': 30,
            'height': 30,
        }
    }
}
