from django.test import TestCase
from thumbnails.conf import settings


class SettingsTest(TestCase):

    def test_load_settings(self):
        self.assertNotEqual(settings.THUMBNAILS, {})
        self.assertNotEqual(settings.SIZES, None)

    def test_get_size(self):
        self.assertEqual(settings.get_size('small'), {'width': 10, 'height': 10})
