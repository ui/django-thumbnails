from django.db.models import ImageField as DjangoImageField

from .files import GalleryFile


class ImageField(DjangoImageField):
    attr_class = GalleryFile
