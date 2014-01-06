import os

from django.core.files import File
from django.test import TestCase

from thumbnails import conf
from thumbnails.files import get_file_path

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
            os.path.join(self.instance.avatar.storage.temporary_location, conf.BASEDIR, 'avatars')

        self.instance.avatar.thumbnails.small

    def tearDown(self):
        self.instance.avatar.storage.delete_temporary_storage()
        super(FilesTest, self).tearDown()

    def test_get_file_path(self):
        self.assertEqual("thumbs/avatars/tests_small.png", get_file_path(self.instance.avatar.name, self.size))
