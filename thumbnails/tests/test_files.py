import os

from django.conf import settings
from django.core.files import File
from django.test import TestCase, override_settings

from thumbnails import conf
from thumbnails.files import populate
from thumbnails.metadata import get_path
from thumbnails.backends.metadata import RedisBackend

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

    def test_populate_non_redis(self):
        test_objc = TestModel.objects.create()
        with open('thumbnails/tests/tests.png', 'rb') as image_file:
            test_objc.avatar = File(image_file)
            test_objc.save()

        # create all thumbnails
        objects = TestModel.objects.all()
        thumbnails = []
        for obj in objects:
            for size in conf.SIZES:
                obj.avatar.thumbnails.get(size)
            thumbnails.append(obj.avatar.thumbnails)

        # reset _thumbnails
        for thumbnail in thumbnails:
            thumbnail._thumbnails = {}

        # default backend(thumbnails.backends.metadata.DatabaseBackend) is not supported
        # skipped all
        self.assertRaises(NotImplementedError, populate, thumbnails)

    def test_populate_redis_backend(self):
        TestModel.objects.all().delete()

        for i in range(1, 10):
            test_objc = TestModel.objects.create()

            with open('thumbnails/tests/tests.png', 'rb') as image_file:
                test_objc.avatar = File(image_file)
                test_objc.save()

        # create all thumbnails
        objects = TestModel.objects.all()
        thumbnails = []
        for obj in objects:
            obj.avatar.thumbnails.metadata_backend = RedisBackend()
            for size in conf.SIZES:
                obj.avatar.thumbnails.get(size)
            thumbnails.append(obj.avatar.thumbnails)

        # reset _thumbnails
        for thumbnail in thumbnails:
            thumbnail._thumbnails = {}

        populate(thumbnails)
        for thumbnail in thumbnails:
            sizes = [size for size in thumbnail._thumbnails.keys()]
            for size in sizes:
                # Make sure all thumbnail sizes have the right value
                self.assertEqual(thumbnail._thumbnails[size].source_name,
                                 thumbnail.source_image.name)
            self.assertEqual(set(sizes), set(conf.SIZES))

    def test_populate_redis_backend_with_size(self):
        TestModel.objects.all().delete()

        for i in range(1, 10):
            test_objc = TestModel.objects.create()

            with open('thumbnails/tests/tests.png', 'rb') as image_file:
                test_objc.avatar = File(image_file)
                test_objc.save()

        # create all thumbnails
        objects = TestModel.objects.all()
        thumbnails = []
        for obj in objects:
            obj.avatar.thumbnails.metadata_backend = RedisBackend()
            for size in conf.SIZES:
                obj.avatar.thumbnails.get(size)
            thumbnails.append(obj.avatar.thumbnails)

        # reset _thumbnails
        for thumbnail in thumbnails:
            thumbnail._thumbnails = {}

        populate(thumbnails, ['small', 'large'])
        for thumbnail in thumbnails:
            sizes = [size for size in thumbnail._thumbnails.keys()]
            for size in sizes:
                # Make sure all thumbnail sizes have the right value
                self.assertEqual(thumbnail._thumbnails[size].source_name,
                                 thumbnail.source_image.name)
            self.assertEqual(set(sizes), set(['small', 'large']))
