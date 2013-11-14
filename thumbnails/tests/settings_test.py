from django.test import TestCase
from thumbnails import conf


class SettingsTest(TestCase):

    def test_load_settings(self):
        self.assertNotEqual(conf.METADATA_BACKEND, None)
        self.assertNotEqual(conf.STORAGE_BACKEND, None)
        self.assertNotEqual(conf.THUMBNAILS, {})
        self.assertNotEqual(conf.SIZES, None)

    def test_get_all_sizes(self):
        self.assertEqual(conf.get_all_sizes(), ['small', 'default', 'large'])

    def test_get_size(self):
        self.assertEqual(conf.get_size('small'), {'width': 10, 'height': 10})
        self.assertEqual(conf.get_size('default'), {'width': 20, 'height': 20})
        self.assertEqual(conf.get_size('large'), {'width': 30, 'height': 30})
