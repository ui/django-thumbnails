import os

from django.core.files import File
from django.test import TestCase

from thumbnails import conf
from thumbnails.metadata import get_path

from .models import TestModel


class FilesTest(TestCase):

    def setUp(self):
        self.source_name = "tests.png"
        self.size = "small"

        self.instance = TestModel.objects.create()
        with open('thumbnails/tests/tests.png', 'rb') as image_file:
            self.instance.avatar = File(image_file)
            self.instance.save()
        self.avatar_folder = \
            os.path.join(self.instance.avatar.storage.temporary_location, conf.BASE_DIR, 'avatars')

        self.instance.avatar.thumbnails.small
        self.basename = os.path.basename(self.instance.avatar.path)
        self.filename, self.ext = os.path.splitext(self.basename)

    def tearDown(self):
        self.instance.avatar.storage.delete_temporary_storage()
        super(FilesTest, self).tearDown()

    def test_get_file_path(self):
        expected_path = os.path.join('thumbs', 'avatars', self.filename + "_small" + self.ext)
        self.assertEqual(expected_path, get_path(self.instance.avatar.name, self.size))
