from django.db import models

from thumbnails.fields import ImageField
from . import storage, metadata


class TestModel(models.Model):
    avatar = ImageField(upload_to='avatars', resize_source_to='source')
    profile_picture = ImageField(upload_to='avatars', blank=True, null=True, resize_source_to='source')
    card_identity_picture = ImageField(upload_to='identity_card', blank=True, null=True,
                                       resize_source_to='source_with_format',
                                       storage=storage.TemporaryStorage2(),
                                       metadata_backend=metadata.CustomRedisBackend())


class TestPregeneratedSizesModel(models.Model):
    logo = ImageField(upload_to='logos', blank=True, null=True, pregenerated_sizes=['small', 'large'])
    photo = ImageField(upload_to='photos', blank=True, null=True, resize_source_to='source_with_format',
                       pregenerated_sizes=['source_with_format', 'default', 'large'])
