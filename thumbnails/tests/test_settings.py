from django.test import TestCase

from thumbnails import conf
from thumbnails.processors import resize


class SettingsTest(TestCase):

    def test_load_settings(self):
        self.assertNotEqual(conf.METADATA, None)
        self.assertNotEqual(conf.STORAGE, None)
        self.assertNotEqual(conf.THUMBNAILS, {})
        self.assertNotEqual(conf.SIZES, {})

    def test_default_processors(self):
        # Make sure default processors override size definition with empty processors
        self.assertEqual(conf.SIZES['small']['processors'], [resize])
