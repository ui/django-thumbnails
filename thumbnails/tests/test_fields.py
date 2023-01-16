import os

from django.core.files import File
from django.template import Context, Template
from django.test import TestCase

from thumbnails import conf
from thumbnails.backends.metadata import RedisBackend, DatabaseBackend
from thumbnails.fields import fetch_thumbnails
from thumbnails.files import Thumbnail, FallbackImage

from .metadata import CustomRedisBackend
from .models import TestModel, TestPregeneratedSizesModel
from .storage import TemporaryStorage2, TemporaryStorage


class ImageFieldTest(TestCase):

    def setUp(self):
        self.instance = TestModel.objects.create()
        # Resize Without Image Convert
        with open('thumbnails/tests/tests.png', 'rb') as image_file:
            self.instance.avatar = File(image_file)
            self.instance.save()
        self.avatar_folder = \
            os.path.join(self.instance.avatar.storage.temporary_location, conf.BASE_DIR, 'avatars')
        self.basename = os.path.basename(self.instance.avatar.path)
        self.filename, self.ext = os.path.splitext(self.basename)

        # Resize with Image Convert
        with open('thumbnails/tests/tests.png', 'rb') as image_file:
            self.instance.card_identity_picture = File(image_file)
            self.instance.save()

        self.identity_card_folder = \
            os.path.join(self.instance.card_identity_picture.storage.temporary_location, conf.BASE_DIR, 'identity_card')
        self.identity_picture_basename = os.path.basename(self.instance.card_identity_picture.path)
        self.identity_filename, self.identity_ext = os.path.splitext(self.identity_picture_basename)

    def tearDown(self):
        self.instance.avatar.storage.delete_temporary_storage()
        self.instance.card_identity_picture.storage.delete_temporary_storage()

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

        # Test convert png image to webp image, ImageField with resize and pregenerated sizes
        self.assertEqual(self.identity_ext, '.webp')

        self.assertIsInstance(thumb.storage, TemporaryStorage)
        self.assertIsInstance(self.instance.avatar.metadata_backend, DatabaseBackend)

        # After convert to webp, make sure resize can be running as normal
        # 1. Test for thumbnail creation
        self.assertFalse(os.path.isfile(os.path.join(self.identity_card_folder, self.identity_filename + '_small' + self.identity_ext)))
        thumb = self.instance.card_identity_picture.thumbnails.create(size='small')
        self.assertTrue(os.path.isfile(os.path.join(self.identity_card_folder, self.identity_filename + '_small' + self.identity_ext)))

        # 2. Test for getting thumbnail
        self.assertEqual(thumb, self.instance.card_identity_picture.thumbnails.get(size='small'))

        # 3. Test for thumbnail deletion
        self.assertTrue(os.path.isfile(os.path.join(self.identity_card_folder, self.identity_filename + '_small' + self.identity_ext)))
        self.instance.card_identity_picture.thumbnails.delete(size='small')
        self.assertFalse(os.path.isfile(os.path.join(self.identity_card_folder, self.identity_filename + '_small' + self.identity_ext)))

        self.assertIsInstance(thumb.storage, TemporaryStorage2)
        self.assertIsInstance(self.instance.card_identity_picture.metadata_backend, CustomRedisBackend)

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

        # Create Thumbnail with source_with_format, formated image with 'webp'
        self.assertEqual(os.path.basename(self.instance.avatar.thumbnails.source_with_format.name),
                         self.filename + '_source_with_format' + '.webp')

        # Make sure ThumbnailManager return the correct thumbnail with Image Convert (webp)
        self.assertTrue(self.instance.card_identity_picture.thumbnails.small, Thumbnail)
        self.assertEqual(os.path.basename(self.instance.card_identity_picture.thumbnails.small.name),
                         self.identity_filename + '_small' + self.identity_ext)
        self.assertTrue(self.instance.card_identity_picture.thumbnails.default, Thumbnail)
        self.assertEqual(os.path.basename(self.instance.card_identity_picture.thumbnails.default.name),
                         self.identity_filename + '_default' + self.identity_ext)
        self.assertTrue(self.instance.card_identity_picture.thumbnails.large, Thumbnail)
        self.assertEqual(os.path.basename(self.instance.card_identity_picture.thumbnails.large.name),
                         self.identity_filename + '_large' + self.identity_ext)

        # Test for name clashing with another file with the same name
        self.instance.card_identity_picture.thumbnails.delete('large')
        open(os.path.join(self.identity_card_folder, 'tests_large.webp'), 'w').close()
        self.instance.card_identity_picture.thumbnails.create('large')

        # Due to uuid4 for file name, this should not clash
        self.assertNotEqual(os.path.basename(self.instance.card_identity_picture.thumbnails.large.name),
                            'tests_large.webp')

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

        # Creating thumbnail should populate the cache correctly (webp)
        source_with_format_thumb = self.instance.avatar.thumbnails.source_with_format
        self.assertEqual(source_with_format_thumb, self.instance.avatar.thumbnails.all().get('source_with_format'))
        # Making sure the file format correctly
        self.assertEqual(os.path.basename(self.instance.avatar.thumbnails.source_with_format.name),
                         self.filename + '_source_with_format' + '.webp')
        self.assertEqual(len(self.instance.avatar.thumbnails._thumbnails), 3)

        # Should also work on deletion
        self.instance.avatar.thumbnails.delete('large')
        self.assertEqual(self.instance.avatar.thumbnails.all().get('large'), None)
        self.assertEqual(len(self.instance.avatar.thumbnails._thumbnails), 2)

        # Should also work on deletion (webp)
        self.instance.avatar.thumbnails.delete('source_with_format')
        self.assertEqual(self.instance.avatar.thumbnails.all().get('source_with_format'), None)
        self.assertEqual(len(self.instance.avatar.thumbnails._thumbnails), 1)

        # Once cached, it should not hit backend on other call.
        with self.assertNumQueries(0):
            self.instance.avatar.thumbnails.default
            self.instance.avatar.thumbnails.all()['default']
            self.instance.avatar.thumbnails.get('default')
            self.instance.avatar.thumbnails.get('default')

        # With Image resize & convert
        # No thumbnails should be cached
        self.assertEqual(self.instance.card_identity_picture.thumbnails._thumbnails, None)

        # Thumbnail with size `default` created and populated to the cache
        self.assertEqual(self.instance.card_identity_picture.thumbnails.default, self.instance.card_identity_picture.thumbnails.all().get('default'))
        self.assertEqual(len(self.instance.card_identity_picture.thumbnails._thumbnails), 1)

        # Creating thumbnail should populate the cache correctly
        large_thumb = self.instance.card_identity_picture.thumbnails.large
        self.assertEqual(large_thumb, self.instance.card_identity_picture.thumbnails.all().get('large'))
        self.assertEqual(len(self.instance.card_identity_picture.thumbnails._thumbnails), 2)

        # Should also work on deletion
        self.instance.card_identity_picture.thumbnails.delete('large')
        self.assertEqual(self.instance.card_identity_picture.thumbnails.all().get('large'), None)
        self.assertEqual(len(self.instance.card_identity_picture.thumbnails._thumbnails), 1)

        # Once cached, it should not hit backend on other call.
        with self.assertNumQueries(0):
            self.instance.card_identity_picture.thumbnails.default
            self.instance.card_identity_picture.thumbnails.all()['default']
            self.instance.card_identity_picture.thumbnails.get('default')
            self.instance.card_identity_picture.thumbnails.get('default')

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

    def test_fetch_non_redis(self):
        test_objc = TestModel.objects.create()
        with open('thumbnails/tests/tests.png', 'rb') as image_file:
            test_objc.avatar = File(image_file)
            test_objc.save()

        # create all thumbnails
        objects = TestModel.objects.all()
        images = []
        for obj in objects:
            for size in conf.SIZES:
                obj.avatar.thumbnails.get(size)
            images.append(obj.avatar)

        # reset _thumbnails
        for image in images:
            image.thumbnails._thumbnails = {}

        # default backend(thumbnails.backends.metadata.DatabaseBackend) is not supported
        self.assertRaises(NotImplementedError, fetch_thumbnails, images)

    def test_fetch_redis_backend(self):
        TestModel.objects.all().delete()

        for i in range(1, 10):
            test_objc = TestModel.objects.create()

            with open('thumbnails/tests/tests.png', 'rb') as image_file:
                test_objc.avatar = File(image_file)
                test_objc.save()

        images = []
        objects = TestModel.objects.all()
        # test pre-created thumbnails
        for obj in objects:
            obj.avatar.thumbnails.metadata_backend = RedisBackend()
            images.append(obj.avatar)

        # make sure cache is still empty, so it can be generated freshly
        fetch_thumbnails(images)
        for image in images:
            self.assertEqual(image.thumbnails._thumbnails, {})

        # create all thumbnails
        for image in images:
            for size in conf.SIZES:
                image.thumbnails.get(size)

        # reset _thumbnails
        for image in images:
            image.thumbnails._thumbnails = {}

        fetch_thumbnails(images)
        for image in images:
            thumbnails = image.thumbnails
            sizes = [size for size in thumbnails._thumbnails.keys()]
            for size in sizes:
                # Make sure all thumbnail sizes have the right value
                self.assertEqual(thumbnails._thumbnails[size].name,
                                 thumbnails.get(size).name)
            self.assertEqual(set(sizes), set(conf.SIZES))

        # Fetch for format image run correctly
        fetch_thumbnails(images, ['source_with_format'])
        for image in images:
            thumbnails = image.thumbnails
            sizes = [size for size in thumbnails._thumbnails.keys()]
            self.assertEqual(thumbnails._thumbnails['source_with_format'].name,
                             thumbnails.get('source_with_format').name)
            self.assertEqual(sizes, ['source_with_format'])
            self.assertEqual(os.path.splitext(thumbnails._thumbnails['source_with_format'].name)[1],
                             '.webp')

    def test_populate_redis_backend_with_size(self):
        TestModel.objects.all().delete()

        for i in range(1, 10):
            test_objc = TestModel.objects.create()

            with open('thumbnails/tests/tests.png', 'rb') as image_file:
                test_objc.avatar = File(image_file)
                test_objc.save()

        # create all thumbnails
        objects = TestModel.objects.all()
        images = []
        for obj in objects:
            obj.avatar.thumbnails.metadata_backend = RedisBackend()
            for size in conf.SIZES:
                obj.avatar.thumbnails.get(size)
            images.append(obj.avatar)

        # reset _thumbnails
        for image in images:
            image.thumbnails._thumbnails = {}

        # Adding format image run correctly
        fetch_thumbnails(images, ['small', 'large', 'source_with_format'])
        for image in images:
            thumbnails = image.thumbnails
            sizes = [size for size in thumbnails._thumbnails.keys()]
            for size in sizes:
                # Make sure all thumbnail sizes have the right value
                self.assertEqual(thumbnails._thumbnails[size].name,
                                 thumbnails.get(size).name)
            self.assertEqual(set(sizes), set(['small', 'large', 'source_with_format']))


class PregeneratedFilesTest(TestCase):
    def setUp(self):
        self.instance = TestPregeneratedSizesModel.objects.create()

    def tearDown(self):
        if self.instance.logo:
            self.instance.logo.storage.delete_temporary_storage()
        if self.instance.photo:
            self.instance.photo.storage.delete_temporary_storage()

        super(PregeneratedFilesTest, self).tearDown()

    def test_image_field(self):
        # Test for thumbanils with pregenerated sizes
        with open('thumbnails/tests/tests.png', 'rb') as image_file:
            self.instance.logo = File(image_file)
            self.instance.save()

        logo_folder = \
            os.path.join(self.instance.logo.storage.temporary_location, conf.BASE_DIR, 'logos')
        logo_basename = os.path.basename(self.instance.logo.path)
        logo_filename, logo_ext = os.path.splitext(logo_basename)

        pregenerated_files = os.listdir(logo_folder)
        self.assertEqual(len(pregenerated_files), 2)
        for size in ['_large', '_small']:
            self.assertIn(logo_filename + size + logo_ext, pregenerated_files)

        # Test for thumbnails with resource to and pregenerated files
        with open('thumbnails/tests/tests.png', 'rb') as image_file:
            self.instance.photo = File(image_file)
            self.instance.save()

        photo_folder = \
            os.path.join(self.instance.photo.storage.temporary_location, conf.BASE_DIR, 'photos')
        photo_basename = os.path.basename(self.instance.photo.path)
        photo_filename, photo_ext = os.path.splitext(photo_basename)

        pregenerated_files = os.listdir(photo_folder)
        self.assertEqual(len(pregenerated_files), 3)
        for size in ['_large', '_default', '_source_with_format']:
            self.assertIn(photo_filename + size + photo_ext, pregenerated_files)
