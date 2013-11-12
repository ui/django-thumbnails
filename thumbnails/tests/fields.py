import os

from django.core.files import File
from django.test import TestCase

from .models import TestModel


class ImageFieldTest(TestCase):

    def setUp(self):
        self.instance = TestModel.objects.create()
        with open('thumbnails/tests/tests.png') as image_file:
            self.instance.avatar = File(image_file)
            self.instance.save()

    def tearDown(self):
        self.instance.avatar.storage.delete_temporary_storage()
        super(ImageFieldTest, self).tearDown()

    def test_image_field(self):
        self.instance.avatar.get_thumbnail(size='small')

        avatar_folder = \
            os.path.join(self.instance.avatar.storage.temporary_location, 'avatars')

        avatars = os.listdir(avatar_folder)
        self.assertTrue('tests_small.png' in avatars)

        self.instance.avatar.delete_thumbnail(size='small')
        avatars = os.listdir(avatar_folder)
        self.assertFalse('tests_small.png' in avatars)
