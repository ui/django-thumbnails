from thumbnails import conf
from thumbnails.utils import import_attribute


def get_backend():
    if not conf.STORAGE.get('BACKEND'):
        raise ValueError('BACKEND for STORAGE must be defined')
    backend = import_attribute(conf.STORAGE['BACKEND'])
    return backend()
