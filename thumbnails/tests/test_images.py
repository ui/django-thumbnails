import os

from django.core.files import File
from django.test import TestCase

from thumbnails import images

from .models import TestModel


class ImageTest(TestCase):

    def setUp(self):
        self.instance = TestModel.objects.create()
        with open('thumbnails/tests/tests.png', 'rb') as image_file:
            self.instance.avatar = File(image_file)
            self.instance.save()

        self.basename = os.path.basename(self.instance.avatar.path)
        self.filename, self.ext = os.path.splitext(self.basename)
        self.source_name = os.path.join('avatars', self.filename + self.ext)

        self.storage_backend = self.instance.avatar.storage
        self.metadata_backend = self.instance.avatar.metadata_backend

    def tearDown(self):
        self.instance.avatar.storage.delete_temporary_storage()
        super(ImageTest, self).tearDown()

    def test_create(self):
        """
        Ensure that ``create`` properly generates the thumbnail
        and its relevant metadata.
        """
        thumbnail_name = images.get_thumbnail_name(self.source_name, 'small')

        self.assertEqual(
            self.metadata_backend.get_thumbnail(self.source_name, 'small'),
            None
        )
        self.assertFalse(self.storage_backend.exists(thumbnail_name))

        thumbnail = images.create(self.source_name, 'small',
                                  self.metadata_backend, self.storage_backend)
        self.assertTrue(self.storage_backend.exists(thumbnail.name))
        self.assertNotEqual(
            self.metadata_backend.get_thumbnail(self.source_name, 'small'),
            None
        )

    def test_get(self):
        """
        Ensure that ``get`` works properly.
        """
        self.assertEqual(
            images.get(self.source_name, 'default',
                       self.metadata_backend, self.storage_backend),
            None
        )
        thumbnail = images.create(self.source_name, 'default',
                                  self.metadata_backend, self.storage_backend)

        self.assertEqual(
            images.get(self.source_name, 'default',
                       self.metadata_backend, self.storage_backend),
            thumbnail
        )

    def test_delete(self):
        """
        Ensure that ``delete`` works properly.
        """
        thumbnail = images.create(self.source_name, 'small',
                                  self.metadata_backend, self.storage_backend)

        images.delete(self.source_name, 'small',
                      self.metadata_backend, self.storage_backend)
        self.assertFalse(self.storage_backend.exists(thumbnail.name))
        self.assertEqual(
            self.metadata_backend.get_thumbnail(self.source_name, 'small'),
            None
        )
