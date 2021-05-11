from da_vinci import images
from PIL import Image


def attach_watermark(image, watermark_path):
    watermark_image = images.from_file(watermark_path)
    if image.get_pil_image().size != watermark_image.get_pil_image.size:
        # TODO: parse watermark dynamically based on ratio
        raise ValueError("Watermark image should have the same dimension as image")

    if watermark_image.format != "PNG":
        raise ValueError("Watermark must be PNG")

    final_image = Image.new("RGBA", image.size)
    final_image = Image.alpha_composite(final_image, image)
    final_image = Image.alpha_composite(final_image, watermark_image)
    return final_image
