import os

from django.core.files import File
from django.db import connection
from django.test import TestCase

from thumbnails.files import Thumbnail
from .models import TestModel
from thumbnails import conf


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
        avatar_folder = \
            os.path.join(self.instance.avatar.storage.temporary_location, conf.BASEDIR, 'avatars')

        # 1. Test for thumbnail creation
        self.assertFalse(os.path.isfile(os.path.join(avatar_folder, 'tests_small.png')))
        thumb = self.instance.avatar.thumbnails.create_thumbnail(size='small')
        self.assertTrue(os.path.isfile(os.path.join(avatar_folder, 'tests_small.png')))

        # Make sure the returned thumbnail is of thumbnail class, not metadata
        self.assertTrue(isinstance(thumb, Thumbnail))
        # 2. Test for getting thumbnail
        self.assertEqual(thumb, self.instance.avatar.thumbnails.get_thumbnail(size='small'))

        # 3. Test for thumbnail deletion
        self.assertTrue(os.path.isfile(os.path.join(avatar_folder, 'tests_small.png')))
        self.instance.avatar.thumbnails.delete_thumbnail(size='small')
        self.assertFalse(os.path.isfile(os.path.join(avatar_folder, 'tests_small.png')))

    def test_thumbnail_field(self):
        # Make sure gallery return the correct thumbnail
        self.assertTrue(self.instance.avatar.thumbnails.small, Thumbnail)
        self.assertEqual(os.path.basename(self.instance.avatar.thumbnails.small.name),
                         'tests_small.png')
        self.assertTrue(self.instance.avatar.thumbnails.default, Thumbnail)
        self.assertEqual(os.path.basename(self.instance.avatar.thumbnails.default.name),
                         'tests_default.png')
        self.assertTrue(self.instance.avatar.thumbnails.large, Thumbnail)
        self.assertEqual(os.path.basename(self.instance.avatar.thumbnails.large.name),
                         'tests_large.png')

    def test_thumbnails_cache(self):

        # No thumbnails should be cached
        self.assertEqual(len(self.instance.avatar.thumbnails._thumbnails), 0)

        # Thumbnail with size `default` created and populated to the cache
        self.assertEqual(self.instance.avatar.thumbnails.default, self.instance.avatar.thumbnails.all().get('default'))
        self.assertEqual(len(self.instance.avatar.thumbnails._thumbnails), 1)

        # Creating thumbnail should populate the cache correctly
        large_thumb = self.instance.avatar.thumbnails.large
        self.assertEqual(large_thumb, self.instance.avatar.thumbnails.all().get('large'))
        self.assertEqual(len(self.instance.avatar.thumbnails._thumbnails), 2)

        # Should also work on deletion
        self.instance.avatar.thumbnails.delete_thumbnail('large')
        self.assertRaises(AttributeError, getattr, self.instance.avatar.thumbnails, '_all_thumbnails')  # cache for all_thumbnails is purged
        self.assertEqual(self.instance.avatar.thumbnails.all().get('large'), None)
        self.assertEqual(len(self.instance.avatar.thumbnails._thumbnails), 1)

        # Once cached, it should not hit backend on other call.
        backend_hit = len(connection.queries)
        self.instance.avatar.thumbnails.default
        self.instance.avatar.thumbnails.all()['default']
        self.instance.avatar.thumbnails.get_thumbnail('default')
        self.assertEqual(backend_hit, len(connection.queries))
