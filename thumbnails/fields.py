from django.db.models.fields.files import ImageFieldFile


class ImageField(ImageFieldFile):

    def __init__(self, *args, **kwargs):
        pass