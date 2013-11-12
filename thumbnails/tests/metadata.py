from django.test import TestCase

from thumbnails.models import Source, ThumbnailMeta
from thumbnails.backends.metadata import DatabaseBackend


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
        source = Source.objects.get(name=source_name)
        self.assertEqual(
            self.backend.get_thumbnail(source_name, 'small'),
            ThumbnailMeta.objects.get(source=source, size='small')
        )
        self.backend.add_thumbnail(source_name, 'large', 'image_large')
        self.assertEqual(
            set(self.backend.get_thumbnails(source_name)),
            {
                ThumbnailMeta.objects.get(source=source, size='small'),
                ThumbnailMeta.objects.get(source=source, size='large')
            }
        )
