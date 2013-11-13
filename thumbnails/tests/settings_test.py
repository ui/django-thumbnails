from django.test import TestCase
from thumbnails.conf import settings


class SettingsTest(TestCase):

    def test_load_settings(self):
        self.assertNotEqual(settings.METADATA_BACKEND, None)
        self.assertNotEqual(settings.STORAGE_BACKEND, None)
        self.assertNotEqual(settings.THUMBNAILS, {})
        self.assertNotEqual(settings.SIZES, None)

    def test_get_all_sizes(self):
        self.assertEqual(settings.get_all_sizes(), ['small', 'default', 'large'])

    def test_get_size(self):
        self.assertEqual(settings.get_size('small'), {'width': 10, 'height': 10})
        self.assertEqual(settings.get_size('default'), {'width': 20, 'height': 20})
        self.assertEqual(settings.get_size('large'), {'width': 30, 'height': 30})
