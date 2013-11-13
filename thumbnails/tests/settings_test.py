from django.test import TestCase
from thumbnails.conf import settings


class SettingsTest(TestCase):

    def test_load_settings(self):
        self.assertNotEqual(settings.THUMBNAILS, {})
        self.assertNotEqual(settings.SIZES, None)
        self.assertEqual(settings.SIZES['small'], {'width': 10, 'height': 10})
        self.assertEqual(settings.SIZES['default'], {'width': 20, 'height': 20})
        self.assertEqual(settings.SIZES['large'], {'width': 30, 'height': 30})
