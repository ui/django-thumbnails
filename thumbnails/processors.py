import io

from django.core.files.base import ContentFile

from da_vinci import images


def resize(image, **kwargs):
    """
    Resized an image based on given width and height
    """
    image.resize(**kwargs)
    return image


def rotate(image, **kwargs):
    """
    Rotates an argument by X degrees.
    """
    image.rotate(**kwargs)
    return image


def flip(image, **kwargs):
    """
    Flips an image. Expects "horizontal" or "vertical" as argument.
    """
    image.flip(**kwargs)
    return image


def crop(image, **kwargs):
    """
    Crops an image based on given width or height
    """
    image.crop(**kwargs)
    return image


def set_quality(image, **kwargs):
    """
    Sets JPG images' quality.
    """
    image.quality = kwargs['quality']
    return image


def add_watermark(image, **kwargs):
    watermark_path = kwargs["watermark_path"]
    watermark_image = images.from_file(watermark_path)
    pil_image = image.get_pil_image()
    watermark_pil_image = watermark_image.get_pil_image()

    if watermark_pil_image.size != pil_image.size:
        # TODO: parse watermark dynamically based on ratio
        raise ValueError("Watermark image should have the same dimension as image")

    if watermark_image.format != "PNG" or watermark_pil_image.mode != "RGBA":
        raise ValueError("Watermark must be PNG and containts alpha")

    pil_image.paste(watermark_pil_image, (0, 0), watermark_pil_image)
    image.set_pil_image(pil_image)

    return image


def process(file, size):
    """
    Process an image through its defined processors
    params :file: filename or file-like object
    params :size: string for size defined in settings
    return a ContentFile
    """
    from . import conf
    # open image in piccaso
    raw_image = images.from_file(file)

    # run through all processors, if defined
    size_dict = conf.SIZES[size]

    # Format image if FORMAT defined in settings
    if 'FORMAT' in size_dict:
        raw_image.format = size_dict['FORMAT']

    for processor in size_dict['PROCESSORS']:
        raw_image = processor['processor'](raw_image, **processor['kwargs'])

    # write to Content File
    image_io = io.BytesIO()
    raw_image.save(file=image_io)
    image_file = ContentFile(image_io.getvalue())

    return image_file
