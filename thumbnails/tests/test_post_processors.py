from django.test import TestCase
from django.core.files import File

from thumbnails.post_processors import optimize


class PostProcessorsTest(TestCase):

    def test_optimize(self):
        with open('thumbnails/tests/tests.png', 'rb') as image_file:
            original_file = File(image_file)
            optimized_file = optimize(
                original_file.file,
                png_command="optipng -force -o7 '%(filename)s' "
            )
            self.assertTrue(original_file.size > optimized_file.size)
