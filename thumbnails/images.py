import os

from django.utils.encoding import force_str

from . import conf
from . import backends
from . import post_processors
from . import processors


class Thumbnail(object):
    """
    An object that contains relevant information about a thumbnailed image.
    """

    def __init__(self, metadata, storage):
        self.metadata = metadata
        self.storage = storage
        self.name = getattr(metadata, 'name', None)

    def __str__(self):
        return force_str(self.name or '')

    def __repr__(self):
        return "<%s: %s>" % (self.__class__.__name__, self.name or "None")

    def __eq__(self, other):
        try:
            return self.__dict__ == other.__dict__
        except AttributeError:
            return False

    def __bool__(self):
        return bool(self.name)

    def check_metadata(self):
        if self.metadata is None:
            raise ValueError('Thumbnail has no source file')

    @property
    def size(self):
        self.check_metadata()
        return self.metadata.size

    @property
    def url(self):
        self.check_metadata()
        return self.storage.url(self.name)


class FallbackImage(object):

    def __init__(self, image_url):
        self.image_url = image_url

    @property
    def url(self):
        return self.image_url


def get_thumbnail_name(source_name, size):
    name, extension = os.path.splitext(source_name)
    if conf.SIZES[size].get("FORMAT"):
        extension = ".{}".format(conf.SIZES[size]['FORMAT'])
    filename = "%s_%s%s" % (name, size, extension)
    return os.path.join(conf.BASE_DIR, filename)


def create(source_name, size, metadata_backend=None, storage_backend=None):
    """
    Creates a thumbnail file and its relevant metadata. Returns a
    Thumbnail instance.
    """
    if storage_backend is None:
        storage_backend = backends.storage.get_backend()
    if metadata_backend is None:
        metadata_backend = backends.metadata.get_backend()

    thumbnail_file = processors.process(storage_backend.open(source_name), size)
    thumbnail_file = post_processors.process(thumbnail_file, size)

    return save(source_name, size, metadata_backend, storage_backend, thumbnail_file)


def save(source_name, size, metadata_backend, storage_backend, image_file):
    name = get_thumbnail_name(source_name, size)
    name = storage_backend.save(name, image_file)

    metadata = metadata_backend.add_thumbnail(source_name, size, name)
    return Thumbnail(metadata=metadata, storage=storage_backend)


def get(source_name, size, metadata_backend=None, storage_backend=None):
    """
    Returns a Thumbnail instance, or None if thumbnail does not yet exist.
    """
    if storage_backend is None:
        storage_backend = backends.storage.get_backend()
    if metadata_backend is None:
        metadata_backend = backends.metadata.get_backend()

    metadata = metadata_backend.get_thumbnail(source_name, size)
    if metadata is None:
        return None
    else:
        return Thumbnail(metadata=metadata, storage=storage_backend)


def delete(source_name, size, metadata_backend=None, storage_backend=None):
    """
    Deletes a thumbnail file and its relevant metadata.
    """
    if storage_backend is None:
        storage_backend = backends.storage.get_backend()
    if metadata_backend is None:
        metadata_backend = backends.metadata.get_backend()

    thumbnail = get(source_name, size, metadata_backend, storage_backend)
    if thumbnail:
        storage_backend.delete(thumbnail.name)

    metadata_backend.delete_thumbnail(source_name, size)
