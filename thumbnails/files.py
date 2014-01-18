import os

from django.db.models.fields.files import ImageFieldFile

from . import conf, post_processors
from .backends.storage import get_backend
from .images import Thumbnail
from . import images
from .processors import process
from .metadata import get_path


class SourceImage(ImageFieldFile):

    def __init__(self, name):
        self.name = name


class ThumbnailedImageFile(ImageFieldFile):

    def __init__(self, instance, field, name, **kwargs):
        super(ThumbnailedImageFile, self).__init__(instance, field, name, **kwargs)
        self.metadata_backend = field.metadata_backend
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
            if not self.source_image:
                return Thumbnail(metadata=None, storage=self.storage)
            return self.get_thumbnail(name)
        else:
            raise AttributeError("'%s' has no attribute '%s'" % (self, name))

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
            metadatas = self.metadata_backend.get_thumbnails(self.source_image.name)

            thumbnails = {}
            for metadata in metadatas:
                thumbnails[metadata.size] = Thumbnail(metadata=metadata, storage=self.storage)

            self._thumbnails = thumbnails
            self._all_thumbnails = thumbnails
        return self._all_thumbnails

    def get_thumbnail(self, size, create=True):
        """
        Returns a Thumbnail instance.
        First check whether thumbnail is already cached. If it doesn't:
        1. Try to fetch the thumbnail
        2. Create thumbnail if it's not present
        3. Cache the thumbnail for future use
        """
        thumbnail = self._thumbnails.get(size)
        
        if thumbnail is None:
            thumbnail = images.get(self.source_image.name, size,
                                   self.metadata_backend, self.storage)

            if thumbnail is None:
                thumbnail = self.create_thumbnail(size)
            
            self._thumbnails[size] = thumbnail
        
        return thumbnail

    def create_thumbnail(self, size):
        """
        Creates and return a thumbnail of a given size.
        """

        thumbnail = images.create(self.source_image.name, size,
                                  self.metadata_backend, self.storage)
        self._purge_all_thumbnails_cache()
        return thumbnail

    def delete_thumbnail(self, size):
        """
        Deletes a thumbnail of a given size
        """
        images.delete(self.source_image.name, size,
                      self.metadata_backend, self.storage)
        self._purge_all_thumbnails_cache()
        del(self._thumbnails[size])


def exists(source_name, size=None):
    path = get_path(source_name, size)
    if path is not None:
        return get_backend().exists(path)
    else:
        return False


def delete(source_name, size=None):
    path = get_path(source_name, size)
    return get_backend().delete(path)
