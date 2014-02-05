from django.test import TestCase
from django.core.files import File
from django.conf import settings

from thumbnails.post_processors import optimize, process


def dummy_post_processor(thumbnail_file):
    thumbnail_file.name = 'DUMMY'
    return thumbnail_file


def smart_post_processor(thumbnail_file):
    thumbnail_file.name = 'SMART'
    return thumbnail_file


class PostProcessorsTest(TestCase):

    def test_process(self):
        POST_PROCESSORS = [{
            'processor': 'thumbnails.tests.test_post_processors.dummy_post_processor',
        }]
        THUMBNAILS = settings.THUMBNAILS
        THUMBNAILS['POST_PROCESSORS'] = POST_PROCESSORS
        with self.settings(THUMBNAILS=THUMBNAILS):
            with open('thumbnails/tests/tests.png', 'rb') as image_file:
                process(image_file)
                self.assertEqual(image_file.name, 'DUMMY')

    def test_optimize(self):
        with open('thumbnails/tests/tests.png', 'rb') as image_file:
            original_file = File(image_file)
            optimized_file = optimize(
                original_file.file,
                png_command="/usr/bin/optipng -force -o7 &> /dev/null '%(filename)s'"
            )
            self.assertTrue(original_file.size > optimized_file.size)
