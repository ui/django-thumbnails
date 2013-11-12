from django.db.models import ImageField as DjangoImageField

from .files import ThumbnailedImageFile


class ImageField(DjangoImageField):
    attr_class = ThumbnailedImageFile
