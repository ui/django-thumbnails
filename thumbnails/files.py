import os

from django.db.models.fields.files import ImageFieldFile

from . import conf
from .backends import metadata
from .backends.storage import get_backend
from .processors import process


class SourceImage(ImageFieldFile):

    def __init__(self, name):
        self.name = name


class ThumbnailedImageFile(ImageFieldFile):

    def __init__(self, instance, field, name, **kwargs):
        super(ThumbnailedImageFile, self).__init__(instance, field, name, **kwargs)
        self.backend = field.backend
        self.thumbnails = Gallery(backend=self.backend,
                                  storage=self.storage,
                                  source_image=self)

    def save(self, name, content, save=True):
        thumbnail = super(ThumbnailedImageFile, self).save(name, content, save)
        self.backend.add_source(self.name)
        return thumbnail


class Gallery(object):

    def __init__(self, backend, storage, source_image):
        self.backend = backend
        self.storage = storage
        self.source_image = source_image
        self._thumbnails = {}

    def __getattr__(self, name):
        if name in conf.SIZES.keys():
            return self.get_thumbnail(name)
        else:
            return super(Gallery, self).__getattr__(name)

    def _get_thumbnail_name(self, size):
        name, extension = os.path.splitext(self.source_image.name)
        filename = "%s_%s%s" % (name, size, extension)
        return os.path.join(conf.BASEDIR, filename)

    def _purge_all_thumbnails_cache(self):
        if hasattr(self, '_all_thumbnails'):
            del self._all_thumbnails

    def all(self):
        # 1. Get all available sizes
        # 2. Return all thumbnails as list
        if not hasattr(self, '_all_thumbnails'):
            metadatas = self.backend.get_thumbnails(self.source_image.name)

            thumbnails = {}
            for metadata in metadatas:
                thumbnails[metadata.size] = Thumbnail(metadata=metadata, storage=self.storage)

            self._thumbnails = thumbnails
            self._all_thumbnails = thumbnails
        return self._all_thumbnails

    def get_thumbnail(self, size, create=True):
        # 1. Get thumbnail metdata from meta store
        # 2. If it doesn't exist, create thumbnail and return it
        thumbnail = self._thumbnails.get(size)
        if thumbnail is None:
            metadata = self.backend.get_thumbnail(self.source_image.name, size)
            if metadata is None:
                thumbnail = self.create_thumbnail(size)
            else:
                thumbnail = Thumbnail(metadata=metadata, storage=self.storage)
            self._thumbnails[size] = thumbnail
        return thumbnail

    def create_thumbnail(self, size):
        # 1. Use Storage API to create a thumbnail (and get its filename)
        # 2. Call metadata_storage.add_thumbnail(self.name, size, filename)
        name = self._get_thumbnail_name(size)

        thumbnail_file = process(self.storage.open(self.source_image.name), size)
        name = self.storage.save(name, thumbnail_file)

        metadata = self.backend.add_thumbnail(self.source_image.name, size, name)
        thumbnail = Thumbnail(metadata=metadata, storage=self.storage)
        self._purge_all_thumbnails_cache()
        return thumbnail

    def delete_thumbnail(self, size):
        # 1. Use Storage API to delete thumbnail
        # 2. Call metadata_storage.remove_thumbnail(self.name, size)
        self.storage.delete(self._get_thumbnail_name(size))
        self.backend.delete_thumbnail(self.source_image.name, size)
        self._purge_all_thumbnails_cache()
        del(self._thumbnails[size])


class Thumbnail(object):
    def __init__(self, metadata, storage):
        self.metadata = metadata
        self.storage = storage

    def __unicode__(self):
        return self.name

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    @property
    def name(self):
        return self.metadata.name

    @property
    def size(self):
        return self.metadata.size

    def url(self):
        return self.storage.url(self.name)


def get_file_path(source_name, size=None):
    if size is None:
        instance = metadata.get_backend().get_source(source_name)
    else:
        instance = metadata.get_backend().get_thumbnail(source_name, size)

    if instance is None:
        return instance
    else:
        return instance.name


def exists(source_name, size=None):
    path = get_file_path(source_name, size)
    if path:
        return get_backend().exists(path)
    else:
        return False


def delete(source_name, size=None):
    path = get_file_path(source_name, size)
    return get_backend().delete(path)
