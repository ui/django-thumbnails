from da_vinci import images

from .utils import write_to_content_file


def attach_watermark(image, watermark_path):
    raw_image = images.from_file(image)
    watermark_image = images.from_file(watermark_path)
    pil_image = raw_image.get_pil_image()
    watermark_pil_image = watermark_image.get_pil_image()
    if pil_image.size != watermark_pil_image.size:
        # TODO: parse watermark dynamically based on ratio
        raise ValueError("Watermark image should have the same dimension as image")

    if watermark_image.format != "PNG" or watermark_pil_image.mode != "RGBA":
        raise ValueError("Watermark must be PNG and containts alpha")

    pil_image.paste(watermark_pil_image, (0, 0), watermark_pil_image)
    raw_image.set_pil_image(pil_image)
    return write_to_content_file(raw_image)
