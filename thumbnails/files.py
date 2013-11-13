import os

from django.db.models.fields.files import ImageFieldFile, FieldFile

from .backends.metadata import DatabaseBackend


class SourceImage(ImageFieldFile):

    def __init__(self, name):
        self.name = name


class ThumbnailedImageFile(FieldFile):

    def __init__(self, *args, **kwargs):
        super(ThumbnailedImageFile, self).__init__(*args, **kwargs)
        self.metadata_backend = DatabaseBackend()

    def _get_thumbnail_name(self, size):
        filename, extension = os.path.splitext(self.name)
        return "%s_%s%s" % (filename, size, extension)

    def get_thumbnail(self, size):
        # 1. Get thumbnail from meta store
        # 2. If it doesn't exist, create thumbnail and return it
        thumbnail = self.metadata_backend.get_thumbnail(self.name, size)
        if thumbnail is None:
            return self.create_thumbnail(size)
        return thumbnail

    def create_thumbnail(self, size):
        # 1. Use Storage API to create a thumbnail (and get its filename)
        # 2. Call metadata_storage.add_thumbnail(self.name, size, filename)
        filename = self._get_thumbnail_name(size)
        self.storage.save(filename, self.file)
        return self.metadata_backend.add_thumbnail(self.name, size, filename)


    def delete_thumbnail(self, size):
        # 1. Use Storage API to delete thumbnail
        # 2. Call metadata_storage.remove_thumbnail(self.name, size)
        self.storage.delete(self._get_thumbnail_name(size))
        self.metadata_backend.delete_thumbnail(self.name, size)

    def save(self, name, content, save=True):
        thumbnail_file = super(ThumbnailedImageFile, self).save(name, content, save)
        self.metadata_backend.add_source(self.name)
        return thumbnail_file
