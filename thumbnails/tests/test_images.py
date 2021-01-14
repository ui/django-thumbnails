import os

from django.core.files import File
from django.test import TestCase

from unittest.mock import patch
from thumbnails import images, conf

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

    def test_get_thumbnail_name(self):
        # test with size in settings
        expected_basename = "%s_%s%s" % (self.filename, "small", self.ext)
        basename = os.path.basename(images.get_thumbnail_name(self.instance.avatar.name, "small"))
        self.assertEqual(basename, expected_basename)

        # test with format
        expected_basename = "%s_%s%s" % (self.filename, "source_with_format", ".webp")
        basename = os.path.basename(images.get_thumbnail_name(self.instance.avatar.name, "source_with_format"))
        self.assertEqual(basename, expected_basename)

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

        # key with format is not defined in settings anymore
        thumbnail = images.create(self.source_name, 'source_with_format',
                                  self.metadata_backend, self.storage_backend)

        thumbnail_size_data = {
            'small': {
                'PROCESSORS': [
                    {'PATH': 'thumbnails.processors.resize', 'width': 10, 'height': 10}
                ]
            },
        }
        with patch('thumbnails.images.conf.SIZES', thumbnail_size_data):
            # ensure error not happening, and its files and metadata are still removed
            images.delete(self.source_name, 'source_with_format',
                          self.metadata_backend, self.storage_backend)
            self.assertFalse(self.storage_backend.exists(thumbnail.name))
            self.assertIsNone(self.metadata_backend.get_thumbnail(self.source_name, 'source_with_format'))

    def test_delete_with_no_thumbnails_file(self):
        avatar_path = self.instance.avatar.path
        avatar_folder = os.path.join(self.instance.avatar.storage.temporary_location, conf.BASE_DIR, 'avatars')
        self.assertTrue(os.path.exists(avatar_path))

        self.instance.avatar.thumbnails.small

        size = 'small'
        thumbnail_name = os.path.basename(images.get_thumbnail_name(self.instance.avatar.name, size))
        thumbnail_path = os.path.join(avatar_folder, thumbnail_name)
        self.assertTrue(os.path.exists(thumbnail_path))

        # test delete non existence thumbnail file, should not raise error
        os.remove(thumbnail_path)
        self.assertFalse(os.path.exists(thumbnail_path))

        images.delete(self.source_name, size,
                      self.metadata_backend, self.storage_backend)

        # thumbnails and their metadata are also deleted
        self.assertEqual(len(os.listdir(avatar_folder)), 0)
        self.assertIsNone(self.metadata_backend.get_thumbnail(self.source_name, size))
