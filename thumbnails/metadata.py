from .backends import metadata


def get_path(source_name, size=None):
    if size is None:
        instance = metadata.get_backend().get_source(source_name)
    else:
        instance = metadata.get_backend().get_thumbnail(source_name, size)

    if instance is None:
        return instance
    else:
        return instance.name
