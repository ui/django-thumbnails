import shortuuid
import os

from django.db.models import ImageField as DjangoImageField

from .backends import metadata, storage
from .files import ThumbnailedImageFile
from . import processors, post_processors


class ImageField(DjangoImageField):
    attr_class = ThumbnailedImageFile

    def __init__(self, *args, **kwargs):
        self.resize_source_to = kwargs.pop('resize_source_to', None)
        if kwargs.get('storage'):
            raise ValueError('Please define storage backend in settings.py instead on the field itself')
        kwargs['storage'] = storage.get_backend()
        self.metadata_backend = metadata.get_backend()
        super(ImageField, self).__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super(ImageField, self).deconstruct()
        del kwargs['storage']
        return name, path, args, kwargs

    def __unicode__(self):
        return self.attname

    def pre_save(self, model_instance, add):
        """
        Process the source image through the defined processors.
        """
        file = getattr(model_instance, self.attname)

        if file and not file._committed:
            image_file = file
            if self.resize_source_to:
                file.seek(0)
                image_file = processors.process(file, self.resize_source_to)
                image_file = post_processors.process(image_file, self.resize_source_to)
            filename = str(shortuuid.uuid()) + os.path.splitext(file.name)[1]
            file.save(filename, image_file, save=False)
        return file

    def south_field_triple(self):
        """
        Return a suitable description of this field for South.
        Taken from smiley chris' easy_thumbnails
        """
        from south.modelsinspector import introspector
        field_class = 'django.db.models.fields.files.ImageField'
        args, kwargs = introspector(self)
        return (field_class, args, kwargs)
