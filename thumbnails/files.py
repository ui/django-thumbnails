import os
import io

from django.core.files.base import ContentFile
from django.db.models.fields.files import ImageFieldFile
from da_vinci import images

from . import conf
from .backends.metadata import DatabaseBackend


class SourceImage(ImageFieldFile):

    def __init__(self, name):
        self.name = name


class ThumbnailedImageFile(ImageFieldFile):
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
        name, extension = os.path.splitext(self.source_image.name)
        return "%s_%s%s" % (name, size, extension)

    def _purge_thumbnails_cache(self):
        if hasattr(self, '_all_thumbnails'):
            del self._all_thumbnails

    def all(self):
        # 1. Get all available sizes
        # 2. Get or create all thumbnails
        # 3. Return all thumbnails as list
        if not hasattr(self, '_all_thumbnails'):
            metadatas = self.metadata_backend.get_thumbnails(self.source_image.name)
            thumbnails = {metadata.size: Thumbnail(metadata=metadata, storage=self.storage) for metadata in metadatas}
            self._thumbnails = thumbnails
            self._all_thumbnails = thumbnails
        return self._all_thumbnails

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
        name = self._get_thumbnail_name(size)

        # open image in piccaso
        image = images.from_file(self.storage.open(self.source_image.name))
        size_dict = conf.SIZES[size]

        # run through all processors, if defined
        for processor in size_dict.get('processors'):
            image = processor(image, **size_dict)

        # save to Storage
        thumbnail_io = io.BytesIO()
        image.save(thumbnail_io)
        thumbnail_file = ContentFile(thumbnail_io.getvalue())
        name = self.storage.save(name, thumbnail_file)

        metadata = self.metadata_backend.add_thumbnail(self.source_image.name, size, name)
        thumbnail = Thumbnail(metadata=metadata, storage=self.storage)
        self._purge_thumbnails_cache()
        return thumbnail

    def delete_thumbnail(self, size):
        # 1. Use Storage API to delete thumbnail
        # 2. Call metadata_storage.remove_thumbnail(self.name, size)
        self.storage.delete(self._get_thumbnail_name(size))
        self.metadata_backend.delete_thumbnail(self.source_image.name, size)
        self._purge_thumbnails_cache()
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
