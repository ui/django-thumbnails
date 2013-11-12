import os

from django.db.models import ImageField as DjangoImageField
from django.core.files.storage import FileSystemStorage
from thumbnails.backends.metadata import DatabaseBackend


class ThumbnailedImageField(DjangoImageField):

    def __init__(self, *args, **kwargs):
        super(ThumbnailedImageField, self).__init__(*args, **kwargs)
        self.backend = DatabaseBackend()
        self.storage = FileSystemStorage()

    def _get_filename(self, size):
        filename, extension = os.path.splitext(self.name)
        return os.path.join([filename, '_', size, extension])

    def get_thumbnail(self, size):
        # 1. Get thumbnail from meta store
        # 2. If it doesn't exist, create thumbnail and return it
        thumbnail = self.backend.get_thumbnail(self.name, size)
        if thumbnail is None:
            return create_thumbnail(size)
        return thumbnail


    def create_thumbnail(self, size):
        # 1. Use Storage API to create a thumbnail (and get its filename)
        # 2. Call metadata_storage.add_thumbnail(self.name, size, filename)
        filename = _get_filename(size)
        self.storage.save(filename, self.file)
        return self.backend.add_thumbnail(self.name, size, filename)


    def delete_thumbnail(self, size):
        # 1. Use Storage API to delete thumbnail
        # 2. Call metadata_storage.remove_thumbnail(self.name, size)
        self.storage.delete(_get_filename(size))
        self.backend.delete_thubnail(self.name, size)
