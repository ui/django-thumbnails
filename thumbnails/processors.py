def resize(image, **kwargs):
    image.resize(width=kwargs['width'], height=kwargs['height'])


def grayscale(image, **kwargs):
    pass


def rotate(image, **kwargs):
    image.rotate(degrees=kwargs['degrees'])


def flip(image, **kwargs):
    image.flip(direction=kwargs['direction'])


def crop(image, **kwargs):
    params = {
        'width': kwargs['width'],
        'height': kwargs['height']
    }
    if kwargs.get('center_offset'):
        params['center_offset'] = kwargs['center_offset']
    if kwargs.get('shape'):
        params['shape'] = kwargs['shape']

    image.crop(**params)
