import os

from django.core.files import File
from django.test import TestCase

from thumbnails import conf
from thumbnails.backends.metadata import RedisBackend
from thumbnails.metadata import get_path
from thumbnails.models import ThumbnailMeta

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
        self.small_metadata_name = os.path.join('thumbs', 'avatars', self.filename + "_" + self.size + self.ext)

    def tearDown(self):
        self.instance.avatar.storage.delete_temporary_storage()
        super(FilesTest, self).tearDown()

    def test_get_file_path(self):
        self.assertEqual(self.small_metadata_name, get_path(self.instance.avatar.name, self.size))

    def test_delete_without_thumbnails(self):
        # delete without thumbnails
        avatar_path = self.instance.avatar.path
        # ensure file still exists
        self.assertTrue(os.path.exists(avatar_path))

        self.instance.avatar.delete(with_thumbnails=False)

        # image file is deleted
        self.assertFalse(os.path.exists(avatar_path))
        # thumbnails and their metadata are not deleted
        self.assertEqual(len(os.listdir(self.avatar_folder)), 1)
        self.assertTrue(ThumbnailMeta.objects.filter(name=self.small_metadata_name).exists())

    def test_delete_with_thumbnails(self):
        avatar_path = self.instance.avatar.path
        # ensure file still exists
        self.assertTrue(os.path.exists(avatar_path))
        self.assertTrue(ThumbnailMeta.objects.filter(name=self.small_metadata_name).exists())

        self.instance.avatar.delete(with_thumbnails=True)

        # image file is deleted
        self.assertFalse(os.path.exists(avatar_path))

        # thumbnails and their metadata are also deleted
        self.assertEqual(len(os.listdir(self.avatar_folder)), 0)
        self.assertFalse(ThumbnailMeta.objects.filter(source__name=self.instance.avatar.name).exists())

    def test_delete_all(self):
        thumbnails = self.instance.avatar.thumbnails

        thumbnails.delete_all()
        # thumbnails and their metadata are deleted
        self.assertEqual(len(os.listdir(self.avatar_folder)), 0)
        self.assertFalse(ThumbnailMeta.objects.filter(source__name=self.instance.avatar.name).exists())


class RedisFilesTest(TestCase):
    def setUp(self):
        self.source_name = "tests.png"
        self.size = "small"

        self.instance = TestModel.objects.create()
        with open('thumbnails/tests/tests.png', 'rb') as image_file:
            self.instance.avatar = File(image_file)
            self.instance.save()
        self.backend = RedisBackend()
        self.instance.avatar.thumbnails.metadata_backend = self.backend
        self.avatar_folder = \
            os.path.join(self.instance.avatar.storage.temporary_location, conf.BASE_DIR, 'avatars')

        self.instance.avatar.thumbnails.small

        self.basename = os.path.basename(self.instance.avatar.path)
        self.filename, self.ext = os.path.splitext(self.basename)

    def tearDown(self):
        key = self.backend.get_thumbnail_key(self.instance.avatar.name)
        self.backend.redis.delete(key)
        self.instance.avatar.storage.delete_temporary_storage()

        super(RedisFilesTest, self).tearDown()

    def test_delete_with_thumbnails(self):
        avatar_path = self.instance.avatar.path
        # ensure file still exists
        self.assertTrue(os.path.exists(avatar_path))

        key = self.backend.get_thumbnail_key(self.instance.avatar.name)
        self.assertTrue(self.backend.redis.exists(key))

        self.instance.avatar.delete(with_thumbnails=True)

        # image file is deleted
        self.assertFalse(os.path.exists(avatar_path))

        # thumbnails and their metadata are also deleted
        self.assertEqual(len(os.listdir(self.avatar_folder)), 0)
        self.assertFalse(self.backend.redis.exists(key))

    def test_delete_all(self):
        thumbnails = self.instance.avatar.thumbnails
        key = self.backend.get_thumbnail_key(self.instance.avatar.name)
        self.assertTrue(self.backend.redis.exists(key))

        thumbnails.delete_all()
        # thumbnails and their metadata are deleted
        self.assertEqual(len(os.listdir(self.avatar_folder)), 0)
        self.assertFalse(self.backend.redis.exists(key))
