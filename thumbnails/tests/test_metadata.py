from redis import StrictRedis
from django.test import TestCase

from thumbnails.backends.metadata import ImageMeta
from thumbnails.models import Source, ThumbnailMeta
from thumbnails.backends.metadata import DatabaseBackend, RedisBackend


class DatabaseBackendTest(TestCase):

    def setUp(self):
        self.backend = DatabaseBackend()

    def test_add_delete_source(self):
        source_name = 'image'
        self.backend.add_source(source_name)
        self.assertTrue(Source.objects.filter(name=source_name).exists())
        self.backend.delete_source(source_name)
        self.assertFalse(Source.objects.filter(name=source_name).exists())

    def test_get_source(self):
        source_name = 'image'
        self.backend.add_source(source_name)
        self.assertEqual(
            self.backend.get_source(source_name),
            Source.objects.get(name=source_name)
        )

    def test_add_delete_thumbnail(self):
        source_name = 'image'
        self.backend.add_source(source_name)
        self.backend.add_thumbnail(source_name, 'small', 'image_small')
        source = Source.objects.get(name=source_name)
        self.assertTrue(ThumbnailMeta.objects.filter(source=source, size='small').exists())
        self.backend.delete_thumbnail(source_name, 'small')
        self.assertFalse(ThumbnailMeta.objects.filter(source=source, size='small').exists())

    def test_get_thumbnail(self):
        source_name = 'image'
        self.backend.add_source(source_name)
        self.backend.add_thumbnail(source_name, 'small', 'image_small')
        self.assertEqual(self.backend.get_thumbnail(source_name, 'small'), ImageMeta(source_name, 'image_small', 'small'))
        self.backend.add_thumbnail(source_name, 'large', 'image_large')

        self.assertEqual(
            self.backend.get_thumbnails(source_name),
            [
                ImageMeta(source_name, 'image_small', 'small'),
                ImageMeta(source_name, 'image_large', 'large')
            ]
        )


class RedisBackendTest(TestCase):

    def setUp(self):
        self.backend = RedisBackend()
        self.redis = StrictRedis()

    def test_get_source_key(self):
        self.assertEqual(self.backend.get_source_key('a.jpg'), 'djthumbs-test:sources:a.jpg')

    def test_get_thumbnail_key(self):
        self.assertEqual(self.backend.get_thumbnail_key('a.jpg'), 'djthumbs-test:thumbnails:a.jpg')

    def test_add_delete_source(self):
        source_name = 'test-thumbnail.jpg'
        source_key = self.backend.get_source_key(source_name)

        self.backend.add_source(source_name)
        self.assertTrue(self.redis.hexists(source_key, source_name))
        self.backend.delete_source(source_name)
        self.assertFalse(self.redis.hexists(source_key, source_name))

    def test_get_source(self):
        source_name = 'test-thumbnail.jpg'
        source_key = self.backend.get_source_key(source_name)

        self.redis.hset(source_key, source_name, source_name)
        self.assertEqual(self.backend.get_source(source_name), source_name)

        # Delete Source
        self.redis.hdel(source_key, source_name)

    def test_add_delete_thumbnail(self):
        source_name = 'test-thumbnail.jpg'
        size = 'small'
        thumbnail_key = self.backend.get_thumbnail_key(source_name)

        self.backend.add_source(source_name)
        self.backend.add_thumbnail(source_name, size, 'test-thumbnail_small.jpg')
        self.assertTrue(self.redis.hexists(thumbnail_key, size))

        self.backend.delete_thumbnail(source_name, size)
        self.assertFalse(self.redis.hexists(thumbnail_key, size))

        # Delete Source
        self.redis.hdel(self.backend.get_source_key(source_name), source_name)

    def test_get_thumbnail(self):
        source_name = 'test-thumbnail.jpg'

        self.backend.add_source(source_name)
        self.backend.add_thumbnail(source_name, 'small', 'test-thumbnail_small.jpg')
        self.assertEqual(self.backend.get_thumbnail(source_name, 'small'), ImageMeta(source_name, 'test-thumbnail_small.jpg', 'small'))
        self.backend.add_thumbnail(source_name, 'large', 'test-thumbnail_large.jpg')

        expected = ['test-thumbnail_large.jpg', 'test-thumbnail_small.jpg']
        result = [image_meta.name for image_meta in self.backend.get_thumbnails(source_name)]
        self.assertEqual(result.sort(), expected.sort())

        # Delete Source & Thumbnails
        thumbnail_key = self.backend.get_thumbnail_key(source_name)
        self.redis.hdel(self.backend.get_source_key(source_name), source_name)
        self.redis.hdel(thumbnail_key, 'small')
        self.redis.hdel(thumbnail_key, 'large')
