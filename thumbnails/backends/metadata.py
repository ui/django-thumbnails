from redis import Redis

from thumbnails.models import Source, ThumbnailMeta


class ImageMeta:

    def __init__(self, source_name, name, size):
        self.source_name = source_name
        self.name = name
        self.size = size

    def __eq__(self, other):
        return self.__dict__ == other.__dict__


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
        source = self.get_source(source_name)
        return ThumbnailMeta.objects.create(source=source, size=size, name=name)

    def delete_thumbnail(self, source_name, size):
        ThumbnailMeta.objects.filter(source__name=source_name, size=size).delete()


class RedisBackend(BaseBackend):
    redis = Redis()

    def get_source_key(name):
        return "djthumbs:sources:%s" % name

    def get_thumbnail_key(name):
        return "djthumbs:thumbnails:%s" % name

    def add_source(self, name):
        self.redis.hset(get_source_key(name), name, name)
        return name

    def get_source(self, name):
        return self.redis.hget(get_source_key(name), name)

    def delete_source(self, name):
        return self.redis.hdel(get_source_key(name), name)

    def get_thumbnails(self, name):
        key = get_thumbnail_key(name)
        metas = self.redis.hgetall(key)
        return [ImageMeta(name, thumbnail_name, size) for size, thumbnail_name in metas.iteritems()]

    def get_thumbnail(self, source_name, size):
        name = self.redis.hget(get_thumbnail_key(name), size)
        if name:
            return ImageMeta(source_name, name, size)
        return None

    def add_thumbnail(self, source_name, size, name):
        self.redis.hset(get_thumbnail_key(name), size, name)
        return ImageMeta(source_name, name, size)

    def delete_thumbnail(self, source_name, size):
        self.redis.hdel(get_thumbnail_key(name), size)
