from django.db import models

from thumbnails.fields import ImageField


class TestModel(models.Model):
    avatar = ImageField(upload_to='avatars')
