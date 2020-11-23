from django.db import models

from thumbnails.fields import ImageField


class TestModel(models.Model):
    avatar = ImageField(upload_to='avatars', resize_source_to='source')
    profile_picture = ImageField(upload_to='avatars', blank=True, null=True, resize_source_to='source')
    card_identity_picture = ImageField(upload_to='identity_card', blank=True, null=True, resize_source_to='source_with_format')
