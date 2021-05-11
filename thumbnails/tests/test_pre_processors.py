import os

from django.test import TestCase
from django.core.files import File
from PIL import Image

from thumbnails.pre_processors import attach_watermark
from thumbnails.utils import write_to_content_file

from .storage import TemporaryStorage


class PreProcessorsTest(TestCase):

    def test_attach_watermark(self):
        image_path = 'thumbnails/tests/tests.png'
        watermark_path = os.path.join(TemporaryStorage().temporary_location, "test_watermark.png") 
        original_image_path = os.path.join(TemporaryStorage().temporary_location, "test_bg.png") 
        watermark_image = Image.open(image_path)

        with open('thumbnails/tests/tests.png', 'rb') as image_file:
            original_file = File(image_file)

            # not rgba
            converted_watermark = watermark_image.convert("RGB")
            converted_watermark.save(watermark_path)

            self.assertRaises(ValueError, attach_watermark, original_file, watermark_path)

        converted_watermark = watermark_image.convert("RGBA")
        converted_watermark.save(watermark_path)

        # different size
        original_image = Image.open(image_path)
        converted_image = original_image.resize((300, 300))
        converted_image.save(original_image_path)

        converted_watermark = converted_watermark.resize((200, 200))
        converted_watermark.save(watermark_path)

        self.assertRaises(ValueError, attach_watermark, original_image_path, watermark_path)

        converted_image = original_image.resize((200, 200))
        converted_image.save(original_image_path)

        # no error raised
        attach_watermark(original_image_path, watermark_path)
