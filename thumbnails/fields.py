from django.db.models import ImageField as DjangoImageField

from .files import ThumbnailedImageFile
from .utils import process_image


class ImageField(DjangoImageField):
    attr_class = ThumbnailedImageFile

    def __init__(self, *args, **kwargs):
        self.resize = kwargs.pop('resize', None)
        super(ImageField, self).__init__(self, *args, **kwargs)

    def pre_save(self, model_instance, add):
        """
        Process the source image through the defined processors.
        """
        file = getattr(model_instance, self.attname)

        if file and not file._committed:
            image_file = file
            if self.resize:
                image_file = process_image(file, self.resize)
            file.save(file.name, image_file, save=False)
        return file
