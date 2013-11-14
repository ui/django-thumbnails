from django.test import TestCase
from thumbnails import conf


class SettingsTest(TestCase):

    def test_load_settings(self):
        self.assertNotEqual(conf.METADATA_BACKEND, None)
        self.assertNotEqual(conf.STORAGE_BACKEND, None)
        self.assertNotEqual(conf.THUMBNAILS, {})
        self.assertNotEqual(conf.SIZES, {})
