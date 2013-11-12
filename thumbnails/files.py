from django.core.files.images import ImageFile
from django.db.models.fields.files import ImageFieldFile


class SourceImage(ImageFieldFile):

    def __init__(self, name):
        self.name = name

    def get_thumbnail(self, size):
        # 1. Get thumbnail from meta store
        # 2. If it doesn't exist, create thumbnail and return it

    def create_thumbnail(self, size):
        # 1. Use Storage API to create a thumbnail (and get its filename)
        # 2. Call metadata_storage.add_thumbnail(self.name, size, filename)

    def delete_thumbnail(self, size):
        # 1. Use Storage API to delete thumbnail
        # 2. Call metadata_storage.remove_thumbnail(self.name, size)
