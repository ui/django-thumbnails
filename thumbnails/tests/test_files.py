import os

from django.core.files import File
from django.test import TestCase

from thumbnails import conf
from thumbnails.files import get_filename, exists, delete
from thumbnails.backends.metadata import DatabaseBackend

from .models import TestModel


class FilesTest(TestCase):

    def setUp(self):
        backend = DatabaseBackend()
        self.source_name = "tests.png"
        self.size = "small"
        self.name = "tests_small.png"

        self.instance = TestModel.objects.create()
        with open('thumbnails/tests/tests.png', 'rb') as image_file:
            self.instance.avatar = File(image_file)
            self.instance.save()
        self.avatar_folder = \
            os.path.join(self.instance.avatar.storage.temporary_location, conf.BASEDIR, 'avatars')

        self.source = backend.add_source(self.source_name)
        self.thumbnail = self.instance.avatar.thumbnails.create_thumbnail(size=self.size)

    def test_get_filename(self):
        self.assertEqual(self.name, get_filename(self.source_name, self.size))

    def test_exists(self):
        self.assertTrue(exists(self.source_name, self.size))
        self.assertFalse(exists(self.source_name, "large"))

    def test_delete(self):
        delete(self.source_name, self.size)
        self.assertFalse(exists(self.source_name, self.size))
