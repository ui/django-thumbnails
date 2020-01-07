from django.db.models.fields.files import ImageFieldFile

from . import conf, images
from .backends.metadata import ImageMeta
from .backends.storage import get_backend
from .images import Thumbnail, FallbackImage
from .metadata import get_path


class SourceImage(ImageFieldFile):

    def __init__(self, name):
        self.name = name


class ThumbnailedImageFile(ImageFieldFile):

    def __init__(self, instance, field, name, **kwargs):
        super(ThumbnailedImageFile, self).__init__(instance, field, name, **kwargs)
        self.metadata_backend = field.metadata_backend
        self.thumbnails = ThumbnailManager(
            metadata_backend=self.metadata_backend,
            storage=self.storage,
            source_image=self
        )

    def save(self, name, content, save=True):
        thumbnail = super(ThumbnailedImageFile, self).save(name, content, save)
        self.metadata_backend.add_source(self.name)
        return thumbnail


class ThumbnailManager(object):
    """A class that manages creation and retrieval of thumbnails."""

    def __init__(self, metadata_backend, storage, source_image):
        self.metadata_backend = metadata_backend
        self.storage = storage
        self.source_image = source_image
        self._thumbnails = None

    def __getattr__(self, name):
        if name in conf.SIZES.keys():
            if not self.source_image:
                fallback_image_url = conf.SIZES[name].get('FALLBACK_IMAGE_URL')
                if fallback_image_url:
                    return FallbackImage(fallback_image_url)
                else:
                    return Thumbnail(metadata=None, storage=self.storage)
            return self.get(name)
        else:
            raise AttributeError("'%s' has no attribute '%s'" % (self, name))

    def _refresh_cache(self):
        """Populate self._thumbnails."""
        self._thumbnails = {}
        metadatas = self.metadata_backend.get_thumbnails(self.source_image.name)
        for metadata in metadatas:
            self._thumbnails[metadata.size] = Thumbnail(metadata=metadata, storage=self.storage)

    def all(self):
        """
        Return all thumbnails in a dict format.
        """
        if self._thumbnails is not None:
            return self._thumbnails
        self._refresh_cache()
        return self._thumbnails

    def get(self, size, create=True):
        """
        Returns a Thumbnail instance.
        First check whether thumbnail is already cached. If it doesn't:
        1. Try to fetch the thumbnail
        2. Create thumbnail if it's not present
        3. Cache the thumbnail for future use
        """
        if self._thumbnails is None:
            self._refresh_cache()

        thumbnail = self._thumbnails.get(size)

        if thumbnail is None:
            thumbnail = images.get(self.source_image.name, size,
                                   self.metadata_backend, self.storage)

            if thumbnail is None:
                thumbnail = self.create(size)

            self._thumbnails[size] = thumbnail

        return thumbnail

    def create(self, size):
        """
        Creates and return a thumbnail of a given size.
        """
        thumbnail = images.create(self.source_image.name, size,
                                  self.metadata_backend, self.storage)
        return thumbnail

    def delete(self, size):
        """
        Deletes a thumbnail of a given size
        """
        images.delete(self.source_image.name, size,
                      self.metadata_backend, self.storage)
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


def populate(model, field_name):
    """
    Regenerate thumnails, so we don't need to use images.get_thumbnail
    when using thumbnails.get(). Currently only support redis backend.
    Thumbnail will be skipped if can't be populated.
    """
    # NOTE: This is just working for redis based backend
    datas = eval("model.objects.exclude(%s=None)" % field_name) # noqa
    try:
        pipeline = eval("datas[0].%s.metadata_backend.redis.pipeline()" % field_name)
    except AttributeError:
        return

    thumbnails = eval("[data.%s.thumbnails for data in datas]" % field_name)
    for thumbnail in thumbnails:
        key = thumbnail.metadata_backend.get_thumbnail_key(thumbnail.source_image.name)
        pipeline.hgetall(key)

    thumbnails_dict = pipeline.execute()

    for thumbnail, data in zip(thumbnails, thumbnails_dict):
        source_name = thumbnail.source_image.name
        thumbnail._thumbnails = {}
        for size, name in data.items():
            thumbnail._thumbnails[size] = ImageMeta(source_name, name, size)

    return thumbnails
