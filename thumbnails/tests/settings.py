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
    'SIZES': {
        'small': {
            'PROCESSORS': [
                {'PATH': 'thumbnails.processors.resize', 'width': 10, 'height': 10}
            ],
            'POST_PROCESSORS': [
                {
                    'PATH': 'thumbnails.post_processors.optimize',
                    'png_command': "optipng -force -o7 '%(filename)s'"
                }
            ]
        },
        'default': {
            'PROCESSORS': [
                {'PATH': 'thumbnails.processors.resize', 'width': 20, 'height': 20},
                {'PATH': 'thumbnails.processors.flip', 'direction': 'horizontal'}
            ],
            'POST_PROCESSORS': [
                {
                    'PATH': 'thumbnails.post_processors.optimize',
                    'png_command': "optipng '%(filename)s'"
                }
            ]
        },
        'large': {
            'PROCESSORS': [
                {'PATH': 'thumbnails.processors.resize', 'width': 80, 'height': 80},
                {'PATH': 'thumbnails.processors.rotate', 'degrees': 45},
                {'PATH': 'thumbnails.processors.crop', 'width': 80, 'height': 80, 'center': ('50%,50%')}
            ]
        },
        'source': {
            'PROCESSORS': [
                {'PATH': 'thumbnails.processors.resize', 'width': 90, 'height': 90}
            ]
        }
    }
}
