try:
    from redis import StrictRedis
except ImportError:
    StrictRedis = None

from thumbnails import compat, conf
from thumbnails.models import Source, ThumbnailMeta
from thumbnails.utils import import_attribute


def get_backend():
    if not conf.METADATA.get('BACKEND'):
        raise ValueError('BACKEND for STORAGE must be defined')
    metadata = import_attribute(conf.METADATA['BACKEND'])
    return metadata()


class ImageMeta:

    def __init__(self, source_name, name, size):
        self.source_name = source_name
        self.name = compat.as_text(name)
        self.size = compat.as_text(size)

    def __eq__(self, other):
        try:
            return self.__dict__ == other.__dict__
        except AttributeError:
            return False


class BaseBackend:

    def add_source(name):
        raise NotImplementedError

    def delete_source(name):
        raise NotImplementedError

    def get_thumbnails(name):
        raise NotImplementedError

    def get_thumbnail(name, size):
        raise NotImplementedError

    def add_thumbnail(name, size, filename):
        raise NotImplementedError

    def delete_thumbnail(name, size):
        raise NotImplementedError

    def flush_thumbnails(name):
        raise NotImplementedError


class DatabaseBackend(BaseBackend):

    def add_source(self, name):
        return Source.objects.create(name=name)

    def get_source(self, name):
        return Source.objects.get(name=name)

    def delete_source(self, name):
        return Source.objects.filter(name=name).delete()

    def get_thumbnails(self, name):
        metas = ThumbnailMeta.objects.filter(source__name=name)
        return [ImageMeta(name, meta.name, meta.size) for meta in metas]

    def get_thumbnail(self, source_name, size):
        try:
            meta = ThumbnailMeta.objects.get(source__name=source_name, size=size)
            return ImageMeta(source_name, meta.name, meta.size)
        except ThumbnailMeta.DoesNotExist:
            return None

    def add_thumbnail(self, source_name, size, name):
        try:
            source = self.get_source(source_name)
        except Source.DoesNotExist:
            # If the source doesn't exist, create it
            # For example when migrating from a regular ImageField to a thumbnailed ImageField
            source = self.add_source(source_name)
        meta = ThumbnailMeta.objects.create(source=source, size=size, name=name)
        return ImageMeta(source_name, meta.name, meta.size)

    def delete_thumbnail(self, source_name, size):
        ThumbnailMeta.objects.filter(source__name=source_name, size=size).delete()

    def flush_thumbnails(self, source_name):
        ThumbnailMeta.objects.filter(source__name=source_name).delete()


class RedisBackend(BaseBackend):

    def __init__(self, host=None, port=None, password=None, db=None, prefix=None):
        host = host or conf.METADATA.get('host', 'localhost')
        port = port or conf.METADATA.get('port', 6379)
        password = password if password is not None else conf.METADATA.get('password', None)
        db = db or conf.METADATA.get('db', 0)
        prefix = prefix if prefix is not None else conf.METADATA.get('PREFIX', 'djthumbs')
        self.prefix = prefix + ":"
        if not StrictRedis:
            msg = "Could not import Redis. Please install 'redis' extra."
            raise ImportError(msg)
        self.redis = StrictRedis(host=host, port=port, password=password, db=db)

    def get_source_key(self, name):
        return "%ssources:%s" % (self.prefix, name)

    def get_thumbnail_key(self, name):
        return "%sthumbnails:%s" % (self.prefix, name)

    def add_source(self, name):
        self.redis.hset(self.get_source_key(name), name, name)
        return name

    def get_source(self, name):
        return compat.as_text(self.redis.hget(self.get_source_key(name), name))

    def delete_source(self, name):
        return self.redis.hdel(self.get_source_key(name), name)

    def get_thumbnails(self, name):
        metas = self.redis.hgetall(self.get_thumbnail_key(name))
        return [ImageMeta(name, thumbnail_name, size) for size, thumbnail_name in metas.items()]

    def get_thumbnail(self, source_name, size):
        name = self.redis.hget(self.get_thumbnail_key(source_name), size)
        if name:
            return ImageMeta(source_name, name, size)
        return None

    def add_thumbnail(self, source_name, size, name):
        self.redis.hset(self.get_thumbnail_key(source_name), size, name)
        return ImageMeta(source_name, name, size)

    def delete_thumbnail(self, source_name, size):
        self.redis.hdel(self.get_thumbnail_key(source_name), size)

    def flush_thumbnails(self, source_name):
        self.redis.delete(self.get_thumbnail_key(source_name))
