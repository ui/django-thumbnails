def resize(image, **kwargs):
    image.resize(width=kwargs['width'], height=kwargs['height'])


def grayscale(image, **kwargs):
    pass


def rotate(image, **kwargs):
    image.rotate(degrees=kwargs['degrees'])


def flip(image, **kwargs):
    image.flip(direction=kwargs['direction'])


def scale(image, **kwargs):
    image.scale(scale=kwargs['scale'])
