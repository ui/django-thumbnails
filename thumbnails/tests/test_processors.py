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
        original_image_path = os.path.join(TemporaryStorage().temporary_location, "test_bg.png") 

        # different size
        original_image_file = images.from_file(image_path)
        original_image = original_image_file.get_pil_image()
        converted_image = original_image.resize((300, 300))
        converted_image.save(original_image_path)
        original_image_file.set_pil_image(converted_image)

        watermark_image = Image.open(image_path)
        converted_watermark = watermark_image.resize((200, 200))
        converted_watermark.save(watermark_path)

        kwargs = {
            "watermark_path": watermark_path
        }
        self.assertRaises(ValueError, add_watermark, original_image_file, **kwargs)

        converted_image = original_image.resize((200, 200))
        converted_image.save(original_image_path)
        original_image_file.set_pil_image(converted_image)

        # not rgba
        converted_watermark = converted_watermark.convert("RGB")
        converted_watermark.save(watermark_path)

        self.assertRaises(ValueError, add_watermark, original_image_file, **kwargs)

        converted_watermark = converted_watermark.convert("RGBA")
        converted_watermark.save(watermark_path)

        # no error raised
        add_watermark(original_image_file, **kwargs)
