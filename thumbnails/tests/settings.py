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
    'METADATA': {
        'PREFIX': 'djthumbs-test',
        'BACKEND': 'thumbnails.backends.metadata.DatabaseBackend',
    },
    'STORAGE': {
        'BACKEND': 'thumbnails.tests.storage.TemporaryStorage'
    },
    'BASEDIR': 'thumbs',
    'DEFAULT_PROCESSORS': ['thumbnails.processors.resize'],
    'SIZES': {
        'small': {
            'width': 10,
            'height': 10,
        },
        'default': {
            'width': 20,
            'height': 20,
            'direction': 'horizontal',
            'processors': ['thumbnails.processors.resize', 'thumbnails.processors.flip'],
        },
        'large': {
            'width': 80,
            'height': 80,
            'degrees': 45,
            'center': '50%,50%',
            'processors': ('thumbnails.processors.resize',
                           'thumbnails.processors.rotate',
                           'thumbnails.processors.crop'),
        },
        'source': {
            'width': 90,
            'height': 90,
            'processors': ['thumbnails.processors.resize']
        }
    }
}
