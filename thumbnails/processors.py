def resize(image, **kwargs):
    image.resize(width=kwargs['width'], height=kwargs['height'])
    return image


def grayscale(image, **kwargs):
    return image


def rotate(image, **kwargs):
    image.rotate(degrees=kwargs['degrees'])
    return image


def flip(image, **kwargs):
    image.flip(direction=kwargs['direction'])
    return image


def crop(image, **kwargs):
    params = {
        'width': kwargs['width'],
        'height': kwargs['height']
    }
    if kwargs.get('center'):
        params['center'] = kwargs['center']
    image.crop(**params)
    return image
