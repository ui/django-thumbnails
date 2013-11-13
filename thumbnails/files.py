import os

from django.db.models.fields.files import ImageFieldFile, FieldFile

from .backends.metadata import DatabaseBackend


class SourceImage(ImageFieldFile):

    def __init__(self, name):
        self.name = name


class ThumbnailedImageFile(FieldFile):
    _thumbnails = {}

    def __init__(self, *args, **kwargs):
        super(ThumbnailedImageFile, self).__init__(*args, **kwargs)
        self.metadata_backend = DatabaseBackend()
        self.thumbnails = Gallery(source=self)

    def all(self):
        # 1. Get all available sizes
        # 2. Get or create all thumbnails
        # 3. Return all thumbnails as list
        raise NotImplementedError()

    def _get_thumbnail_name(self, size):
        filename, extension = os.path.splitext(self.name)
        return "%s_%s%s" % (filename, size, extension)

    def _get_thumbnails(self, size, metadata):
        """
        Cache thumbnail instances
        """
        thumbnail = self._thumbnails.get(size)
        if thumbnail is None:
            thumbnail = ThumbnailedFile(instance=self.instance,
                                        field=self.field,
                                        name=metadata.name)
            self._thumbnails[size] = thumbnail
        return thumbnail

    def get_thumbnail(self, size):
        # 1. Get thumbnail from meta store
        # 2. If it doesn't exist, create thumbnail and return it
        metadata = self.metadata_backend.get_thumbnail(self.name, size)
        if metadata is None:
            return self.create_thumbnail(size)
        else:
            return self._get_thumbnails(size, metadata)

    def create_thumbnail(self, size):
        # 1. Use Storage API to create a thumbnail (and get its filename)
        # 2. Call metadata_storage.add_thumbnail(self.name, size, filename)
        filename = self._get_thumbnail_name(size)
        self.storage.save(filename, self.file)
        metadata = self.metadata_backend.add_thumbnail(self.name, size, filename)
        thumbnail = ThumbnailedFile(instance=self.instance, field=self.field, name=metadata.name)
        self._thumbnails[size] = thumbnail
        return thumbnail


    def delete_thumbnail(self, size):
        # 1. Use Storage API to delete thumbnail
        # 2. Call metadata_storage.remove_thumbnail(self.name, size)
        self.storage.delete(self._get_thumbnail_name(size))
        self.metadata_backend.delete_thumbnail(self.name, size)
        del(self._thumbnails[size])


    def save(self, name, content, save=True):
        thumbnail = super(ThumbnailedImageFile, self).save(name, content, save)
        self.metadata_backend.add_source(self.name)
        return thumbnail


class Gallery(object):

    def __init__(self, *args, **kwargs):
        self.source = kwargs.pop('source')
        super(Gallery, self).__init__(*args, **kwargs)

    def __getattr__(self, name):
        if name == "small":
            return self.get_thumbnail(name)

    def all(self):
        return self.source.all()

    def get_thumbnail(self, size):
        return self.source.get_thumbnail(size)

    def create_thumbnail(self, size):
        return self.source.create_thumbnail(size)

    def delete_thumbnail(self, size):
        return self.source.delete_thumbnail(size)


class ThumbnailedFile(FieldFile):
    """
    Class for thumbnail image, restriction on save and delete are copied from
    SmileyChris' easy_thumbnails.files.ThumbnailFile
    """
    def __init__(self, instance, field, name, *args, **kwargs):
        super(ThumbnailedFile, self).__init__(instance, field, name)

    def save(self, *args, **kwargs):
        # Can't save a ``ThumbnailFile`` directly.
        raise NotImplementedError()

    def delete(self, *args, **kwargs):
        # Can't delete a ``ThumbnailFile`` directly, it doesn't have a
        # reference to the source image, so it can't update the cache. If you
        # really need to do this, do it with ``self.storage.delete`` directly.
        raise NotImplementedError()
