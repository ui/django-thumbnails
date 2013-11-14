from picasso import images


def resize(source, width, height, filename):
    image = images.from_file(source)
    image.resize(width=width, height=height)
    source.seek(0)
    return image

