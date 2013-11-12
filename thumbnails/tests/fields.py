from django.db import models
from django.test import TestCase

from .models import TestModel


class ImageFieldTest(TestCase):

    def setUp(self):
        self.instance = TestModel.objects.create(avatar='thumbnails/tests/tests.png')

    def test_image_field(self):
        print self.instance.avatar.__class__
        self.instance.avatar.get_thumbnail(size='small')
