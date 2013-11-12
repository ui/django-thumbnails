import os

from django.core.files import File
from django.test import TestCase

from .models import TestModel
from .storage import TemporaryStorage


class ImageFieldTest(TestCase):

    def setUp(self):
        self.storage = TemporaryStorage()

        with open('thumbnails/tests/tests.png') as image_file:
            self.storage.save('tests.png', File(image_file))

        self.instance = TestModel.objects.create(avatar='tests.png')
        self.instance.avatar.storage = self.storage

    def tearDown(self):
        self.storage.delete_temporary_storage()
        super(ImageFieldTest, self).tearDown()

    def test_image_field(self):
        avatar = self.instance.avatar.get_thumbnail(size='small')

        avatars = os.listdir(self.storage.temporary_location)
        self.assertTrue('tests_small.png' in avatars)

        self.instance.avatar.delete_thumbnail(size='small')
        avatars = os.listdir(self.storage.temporary_location)
        self.assertFalse('tests_small.png' in avatars)
