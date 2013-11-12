from django.db import models

from thumbnails.fields import ThumbnailedImageField


class TestModel(models.Model):
    avatar = ThumbnailedImageField(upload_to='avatars')
