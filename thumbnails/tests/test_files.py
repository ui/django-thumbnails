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

        self.basename = os.path.basename(self.instance.avatar.path)
        self.filename, self.ext = os.path.splitext(self.basename)

    def tearDown(self):
        self.instance.avatar.storage.delete_temporary_storage()
        super(FilesTest, self).tearDown()

    def test_get_file_path(self):
        self.instance.avatar.thumbnails.small
        expected_path = os.path.join('thumbs', 'avatars', self.filename + "_small" + self.ext)
        self.assertEqual(expected_path, get_path(self.instance.avatar.name, self.size))

    def test_delete_without_thumbnails(self):
        self.instance.avatar.thumbnails.small

        # delete without thumbnails
        avatar_path = self.instance.avatar.path
        # ensure file still exists
        self.assertTrue(os.path.exists(avatar_path))

        metadata_name = os.path.join('thumbs', 'avatars', self.filename + "_small" + self.ext)

        self.instance.avatar.delete(with_thumbnails=False)

        # image file is deleted
        self.assertFalse(os.path.exists(avatar_path))
        # thumbnails and their metadata are not deleted
        self.assertEqual(len(os.listdir(self.avatar_folder)), 1)
        self.assertTrue(ThumbnailMeta.objects.filter(name=metadata_name).exists())

    def test_delete_with_thumbnails_redis(self):
        avatar_path = self.instance.avatar.path
        # ensure file still exists
        self.assertTrue(os.path.exists(avatar_path))

        backend = RedisBackend()

        self.instance.avatar.thumbnails.metadata_backend = backend
        key = backend.get_thumbnail_key(self.instance.avatar.name)

        self.instance.avatar.thumbnails.small
        self.assertIsNotNone(backend.redis.hgetall(key)[self.size.encode()])

        self.instance.avatar.delete()

        # image file is deleted
        self.assertFalse(os.path.exists(avatar_path))

        # thumbnails and their metadata are also deleted
        self.assertEqual(len(os.listdir(self.avatar_folder)), 0)
        self.assertFalse(backend.redis.exists(key))
