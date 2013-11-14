import os

from django.db.models.fields.files import ImageFieldFile, FieldFile

from .backends.metadata import DatabaseBackend
from . import conf


class SourceImage(ImageFieldFile):

    def __init__(self, name):
        self.name = name


class ThumbnailedImageFile(FieldFile):
    _thumbnails = {}

    def __init__(self, *args, **kwargs):
        super(ThumbnailedImageFile, self).__init__(*args, **kwargs)
        self.metadata_backend = DatabaseBackend()
        self.thumbnails = Gallery(metadata_backend=self.metadata_backend,
                                  storage=self.storage,
                                  source_image=self)

    def save(self, name, content, save=True):
        thumbnail = super(ThumbnailedImageFile, self).save(name, content, save)
        self.metadata_backend.add_source(self.name)
        return thumbnail


class Gallery(object):

    def __init__(self, metadata_backend, storage, source_image):
        self.metadata_backend = metadata_backend
        self.storage = storage
        self.source_image = source_image
        self._thumbnails = {}

    def __getattr__(self, name):
        if name in conf.SIZES.keys():
            return self.get_thumbnail(name)
        else:
            return super(Gallery, self).__getattr__(name)

    def _get_thumbnail_name(self, size):
        filename, extension = os.path.splitext(self.source_image.name)
        return "%s_%s%s" % (filename, size, extension)

    def all(self):
        # 1. Get all available sizes
        # 2. Get or create all thumbnails
        # 3. Return all thumbnails as list
        if not hasattr(self, '_thumbnails'):
            metadatas = self.metadata_backend.get_thumbnails(self.source_image.name)
            thumbnails = {metadata.size: Thumbnail(metadata=metadata, storage=self.storage) for metadata in metadatas}
            self._thumbnails = thumbnails
        return self._thumbnails

    def get_thumbnail(self, size, create=True):
        # 1. Get thumbnail metdata from meta store
        # 2. If it doesn't exist, create thumbnail and return it
        thumbnail = self._thumbnails.get(size)
        if thumbnail is None:
            metadata = self.metadata_backend.get_thumbnail(self.source_image.name, size)
            if metadata is None:
                thumbnail = self.create_thumbnail(size)
            else:
                thumbnail = Thumbnail(metadata=metadata, storage=self.storage)
                self._thumbnails[size] = thumbnail
        return thumbnail

    def create_thumbnail(self, size):
        # 1. Use Storage API to create a thumbnail (and get its filename)
        # 2. Call metadata_storage.add_thumbnail(self.name, size, filename)
        filename = self._get_thumbnail_name(size)
        self.storage.save(filename, self.source_image.file)
        metadata = self.metadata_backend.add_thumbnail(self.source_image.name, size, filename)
        thumbnail = Thumbnail(metadata=metadata, storage=self.storage)
        self._thumbnails[size] = thumbnail
        return thumbnail

    def delete_thumbnail(self, size):
        # 1. Use Storage API to delete thumbnail
        # 2. Call metadata_storage.remove_thumbnail(self.name, size)
        self.storage.delete(self._get_thumbnail_name(size))
        self.metadata_backend.delete_thumbnail(self.source_image.name, size)
        del(self._thumbnails[size])


class Thumbnail(object):
    def __init__(self, metadata, storage):
        self.metadata = metadata
        self.storage = storage

    def __unicode__(self):
        return self.name

    @property
    def name(self):
        return self.metadata.name

    @property
    def size(self):
        return self.metadata.size

    def url(self):
        return self.storage.url(self.name)
