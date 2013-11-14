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
    'SIZES': {
        'small': {
            'width': 10,
            'height': 10,
            'processors': ['thumbnails.processors.resize', 'thumbnails.processors.grayscale'],
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
