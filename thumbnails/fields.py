import shortuuid
import os

from django.db.models import ImageField as DjangoImageField

from thumbnails import compat

from .backends import metadata, storage
from .backends.metadata import ImageMeta
from .files import ThumbnailedImageFile
from .images import Thumbnail, save
from . import processors, post_processors, conf


class ImageField(DjangoImageField):
    attr_class = ThumbnailedImageFile

    def __init__(self, *args, **kwargs):
        self.resize_source_to = kwargs.pop('resize_source_to', None)
        self.pregenerated_sizes = kwargs.pop('pregenerated_sizes', [])
        self.storage_backend = kwargs.get('storage') or storage.get_backend()
        self.metadata_backend = kwargs.pop('metadata_backend', None) or metadata.get_backend()
        kwargs['storage'] = self.storage_backend
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
            original_filename = file.name
            file_type = os.path.splitext(original_filename)[1]

            if self.resize_source_to:
                file.seek(0)
                image_file = processors.process(file, self.resize_source_to)
                image_file = post_processors.process(image_file, self.resize_source_to)

                if 'FORMAT' in conf.SIZES[self.resize_source_to]:
                    file_type = ".{}".format(conf.SIZES[self.resize_source_to]['FORMAT'])

            filename = str(shortuuid.uuid()) + file_type
            file.save(filename, image_file, save=False)

            for size in self.pregenerated_sizes:
                if size == self.resize_source_to:
                    # no need to process file if it is in resize_source_to,
                    # since it had been processed right before this
                    save(file.name, size, self.metadata_backend,
                         self.storage_backend, image_file)
                    continue
                file.thumbnails.create(size)

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


def fetch_thumbnails(images, sizes=None):
    """
    Regenerate EXISTING thumbnails, so we don't need to call redis when using
    thumbnails.get() or thumbnails.all(). Currently only support redis backend.
    NotImeplementedError will be raised, if backend is not supported
    """
    # NOTE: This is just working for redis based backend and same backend
    # different backend among thumbnails may results in bugs
    if not images:
        return

    backend = images[0].thumbnails.metadata_backend
    try:
        pipeline = backend.redis.pipeline()
    except AttributeError:
        raise NotImplementedError('Only Redis metadata backend is implemented')

    for image in images:
        thumbnails = image.thumbnails
        key = thumbnails.metadata_backend.get_thumbnail_key(thumbnails.source_image.name)
        if sizes:
            pipeline.hmget(key, sizes)
        else:
            pipeline.hgetall(key)

    # if sizes is provided results will be list of lists, else it will be list of dicts
    results = pipeline.execute()
    for image, data in zip(images, results):
        thumbnails = image.thumbnails
        source_name = thumbnails.source_image.name
        thumbnails._thumbnails = {}

        if sizes:
            # data shold be list, thus group it with its size beforehand
            items = zip(sizes, data)
        else:
            # data should be dict
            items = data.items()

        for size, name in items:
            if not name:
                continue
            image_meta = ImageMeta(source_name, name, size)
            thumbnails._thumbnails[compat.as_text(size)] = Thumbnail(image_meta, thumbnails.storage)
