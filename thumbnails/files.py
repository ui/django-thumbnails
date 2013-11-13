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

    def __init__(self, *args, **kwargs):
        self.metadata_backend = kwargs.pop('metadata_backend')
        self.storage = kwargs.pop('storage')
        self.source_image = kwargs.pop('source_image')
        self._thumbnails = {}

    def __getattr__(self, name):
        if name in conf.SIZES.keys():
            return self.get_thumbnail(name)
        else:
            return super(Gallery, self).__getattr__(name)

    def _get_thumbnail_name(self, size):
        filename, extension = os.path.splitext(self.source_image.name)
        return "%s_%s%s" % (filename, size, extension)

    def _get_thumbnails(self, size, metadata):
        """
        Cache thumbnail instances
        """
        thumbnail = self._thumbnails.get(size)
        if thumbnail is None:
            thumbnail = ThumbnailedFile(metadata=metadata, storage=self.storage)
            self._thumbnails[size] = thumbnail
        return thumbnail

    def _purge_thumbnails_cache(self):
        if hasattr(self, '_all_thumbnails'):
            del self._all_thumbnails

    def all(self):
        # 1. Get all available sizes
        # 2. Get or create all thumbnails
        # 3. Return all thumbnails as list
        if not hasattr(self, '_all_thumbnails'):
            metadatas = self.metadata_backend.get_thumbnails(self.source_image.name)
            thumbnails = [ThumbnailedFile(metadata=metadata, storage=self.storage) for metadata in metadatas]
            self._all_thumbnails = thumbnails
        return self._thumbnails

    def get_thumbnail(self, size, create=True):
        # 1. Get thumbnail metdata from meta store
        # 2. If it doesn't exist, create thumbnail and return it
        metadata = self.metadata_backend.get_thumbnail(self.source_image.name, size)
        if metadata is None:
            if create:
                return self.create_thumbnail(size)
            else:
                return None
        else:
            return self._get_thumbnails(size, metadata)

    def create_thumbnail(self, size):
        # 1. Use Storage API to create a thumbnail (and get its filename)
        # 2. Call metadata_storage.add_thumbnail(self.name, size, filename)
        filename = self._get_thumbnail_name(size)
        self.storage.save(filename, self.source_image.file)
        metadata = self.metadata_backend.add_thumbnail(self.source_image.name, size, filename)
        thumbnail = ThumbnailedFile(metadata=metadata, storage=self.storage)
        self._thumbnails[size] = thumbnail
        self._purge_thumbnails_cache()
        return thumbnail

    def delete_thumbnail(self, size):
        # 1. Use Storage API to delete thumbnail
        # 2. Call metadata_storage.remove_thumbnail(self.name, size)
        self.storage.delete(self._get_thumbnail_name(size))
        self.metadata_backend.delete_thumbnail(self.source_image.name, size)
        self._purge_thumbnails_cache()
        del(self._thumbnails[size])


class ThumbnailedFile(object):
    def __init__(self, *args, **kwargs):
        self.metadata = kwargs.pop('metadata')
        self.storage = kwargs.pop('storage')

    def __unicode__(self):
        return self.name

    @property
    def name(self):
        return self.metadata.name

    def url(self):
        return self.storage.url(self.name)
