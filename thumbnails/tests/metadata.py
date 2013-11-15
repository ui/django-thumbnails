import redis, json
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
        self.con = redis.StrictRedis(host='localhost', port=6379, db=0)

    def test_add_delete_source(self):
        source_name = 'image.jpg'
        self.backend.add_source(source_name)
        self.assertEqual(self.con.get("source:%s" % source_name), '{}')
        self.backend.delete_source(source_name)
        self.assertEqual(self.con.get("source:%s" % source_name), None)

    def test_get_source(self):
        source_name = 'image.jpg'
        self.backend.add_source(source_name)
        self.assertEqual(self.backend.get_source(source_name), {})

    def test_add_delete_thumbnail(self):
        source_name = 'image.jpg'
        name = 'image_small.jpg'
        size = 'small'
        expected = {
            'image.jpg_small': {
                'name': name,
                'size': size
            }
        }

        self.backend.add_source(source_name)
        self.backend.add_thumbnail(source_name, size, name)
        self.assertEqual(self.con.get("source:%s" % source_name), json.dumps(expected))

        self.backend.delete_thumbnail(source_name, size)
        self.assertEqual(self.con.get("source:%s" % source_name), '{}')

    def test_get_thumbnail(self):
        source_name = 'image.jpg'

        self.backend.add_source(source_name)
        self.backend.add_thumbnail(source_name, 'small', 'image_small.jpg')
        self.assertEqual(self.backend.get_thumbnail(source_name, 'small'), ImageMeta(source_name, 'image_small.jpg', 'small'))
        self.backend.add_thumbnail(source_name, 'large', 'image_large.jpg')

        self.assertEqual(
            self.backend.get_thumbnails(source_name),
            [
                ImageMeta(source_name, 'image_small.jpg', 'small'),
                ImageMeta(source_name, 'image_large.jpg', 'large')
            ]
        )

