import os

from django.core.files import File
from django.template import Context, Template
from django.test import TestCase

from thumbnails import conf
from thumbnails.files import Thumbnail, FallbackImage

from .models import TestModel


class ImageFieldTest(TestCase):

    def setUp(self):
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
        super(ImageFieldTest, self).tearDown()

    def test_image_field(self):

        # 1. Test for thumbnail creation
        self.assertFalse(os.path.isfile(os.path.join(self.avatar_folder, self.filename + '_small' + self.ext)))
        thumb = self.instance.avatar.thumbnails.create(size='small')
        self.assertTrue(os.path.isfile(os.path.join(self.avatar_folder, self.filename + '_small' + self.ext)))

        # Make sure the returned thumbnail is of thumbnail class, not metadata
        self.assertTrue(isinstance(thumb, Thumbnail))
        # 2. Test for getting thumbnail
        self.assertEqual(thumb, self.instance.avatar.thumbnails.get(size='small'))

        # 3. Test for thumbnail deletion
        self.assertTrue(os.path.isfile(os.path.join(self.avatar_folder, self.filename + '_small' + self.ext)))
        self.instance.avatar.thumbnails.delete(size='small')
        self.assertFalse(os.path.isfile(os.path.join(self.avatar_folder, self.filename + '_small' + self.ext)))

    def test_thumbnail_field(self):
        # Make sure ThumbnailManager return the correct thumbnail
        self.assertTrue(self.instance.avatar.thumbnails.small, Thumbnail)

        self.assertEqual(os.path.basename(self.instance.avatar.thumbnails.small.name),
                         self.filename + '_small' + self.ext)
        self.assertTrue(self.instance.avatar.thumbnails.default, Thumbnail)
        self.assertEqual(os.path.basename(self.instance.avatar.thumbnails.default.name),
                         self.filename + '_default' + self.ext)
        self.assertTrue(self.instance.avatar.thumbnails.large, Thumbnail)
        self.assertEqual(os.path.basename(self.instance.avatar.thumbnails.large.name),
                         self.filename + '_large' + self.ext)

        # Test for name clashing with another file with the same name
        self.instance.avatar.thumbnails.delete('large')
        open(os.path.join(self.avatar_folder, 'tests_large.png'), 'w').close()
        self.instance.avatar.thumbnails.create('large')

        # Due to uuid4 for file name, this should not clash
        self.assertNotEqual(os.path.basename(self.instance.avatar.thumbnails.large.name),
                            'tests_large.png')

    def test_thumbnails_cache(self):

        # No thumbnails should be cached
        self.assertEqual(self.instance.avatar.thumbnails._thumbnails, None)

        # Thumbnail with size `default` created and populated to the cache
        self.assertEqual(self.instance.avatar.thumbnails.default, self.instance.avatar.thumbnails.all().get('default'))
        self.assertEqual(len(self.instance.avatar.thumbnails._thumbnails), 1)

        # Creating thumbnail should populate the cache correctly
        large_thumb = self.instance.avatar.thumbnails.large
        self.assertEqual(large_thumb, self.instance.avatar.thumbnails.all().get('large'))
        self.assertEqual(len(self.instance.avatar.thumbnails._thumbnails), 2)

        # Should also work on deletion
        self.instance.avatar.thumbnails.delete('large')
        self.assertEqual(self.instance.avatar.thumbnails.all().get('large'), None)
        self.assertEqual(len(self.instance.avatar.thumbnails._thumbnails), 1)

        # Once cached, it should not hit backend on other call.
        with self.assertNumQueries(0):
            self.instance.avatar.thumbnails.default
            self.instance.avatar.thumbnails.all()['default']
            self.instance.avatar.thumbnails.get('default')
            self.instance.avatar.thumbnails.get('default')

    def test_django_template(self):
        template = Template("Test render {{ image.thumbnails.large.url }} ")
        context = Context({"image": self.instance.avatar})
        result = template.render(context)
        expected_path = os.path.join('thumbs', 'avatars', self.filename + "_large" + self.ext)
        self.assertIn(expected_path, result)

    def test_thumbnails_without_source(self):
        template = Template("Test render {{ image.thumbnails.large.url }} ")

        test_model = TestModel.objects.create()
        test_model.avatar = None
        test_model.save()
        context = Context({"image": test_model.avatar})
        self.assertRaises(ValueError, template.render, context)

        test_model = TestModel.objects.create()
        test_model.avatar = ''
        test_model.save()
        context = Context({"image": test_model.avatar})
        self.assertRaises(ValueError, template.render, context)

        # If source_image is None, ValueError should be raised when calling functions
        # AttributeError must be raised if ThumbnailManager is called with non existent size
        # This applies when no default picture is defined
        self.assertFalse(test_model.avatar)
        self.assertRaises(ValueError, getattr, test_model.avatar.thumbnails.large, 'url')
        self.assertRaises(AttributeError, getattr, test_model.avatar.thumbnails, 'lrge')

    def test_fallback_image(self):

        # We have defined FALLBACK_IMAGE_URL for size ``default``
        self.assertFalse(self.instance.profile_picture)
        self.assertTrue(isinstance(self.instance.profile_picture.thumbnails.default, FallbackImage))

        # No errors should be raised when url attribute
        self.instance.profile_picture.thumbnails.default.url

        # No FALLBACK_IMAGE_URL defined for size ``large``
        self.assertFalse(self.instance.profile_picture)
        self.assertTrue(isinstance(self.instance.profile_picture.thumbnails.large, Thumbnail))

        # Error should be raised when calling url attribute
        self.assertRaises(ValueError, getattr, self.instance.profile_picture.thumbnails.large, 'url')
        self.assertRaises(ValueError, getattr, self.instance.profile_picture.thumbnails.large, 'size')

    def test_resize_source_to_none(self):
        # Make sure that fields without resize_source_to does not raise error on save
        with open('thumbnails/tests/tests.png', 'rb') as image_file:
            self.instance.profile_picture = File(image_file)
            self.instance.save()
