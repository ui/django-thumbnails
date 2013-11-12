from django.db import models

from thumbnails.fields import ImageField
from .storage import TemporaryStorage

class TestModel(models.Model):
    avatar = ImageField(storage=TemporaryStorage(), upload_to='avatars')
