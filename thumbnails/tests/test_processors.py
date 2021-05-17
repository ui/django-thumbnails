import os

from da_vinci import images
from django.test import TestCase
from django.core.files import File
from PIL import Image

from thumbnails.processors import add_watermark

from .storage import TemporaryStorage


class ProcessorsTest(TestCase):

    def test_add_watermark(self):
        image_path = 'thumbnails/tests/tests.png'
        watermark_path = os.path.join(TemporaryStorage().temporary_location, "test_watermark.png") 

        # different size
        original_image_file = images.from_file(image_path)

        watermark_image = Image.open(image_path)
        converted_watermark = watermark_image.resize((200, 200))
        converted_watermark.save(watermark_path)

        kwargs = {
            "width": 300,
            "height": 300,
            "path": watermark_path
        }
        self.assertRaises(ValueError, add_watermark, original_image_file, **kwargs)

        # not rgba
        converted_watermark = converted_watermark.convert("RGB")
        converted_watermark.save(watermark_path)

        kwargs["width"] = 200
        kwargs["height"] = 200
        self.assertRaises(ValueError, add_watermark, original_image_file, **kwargs)

        converted_watermark = converted_watermark.convert("RGBA")
        converted_watermark.save(watermark_path)

        # no error raised
        add_watermark(original_image_file, **kwargs)
