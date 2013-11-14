import redis, json
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
    con = redis.StrictRedis(host='localhost', port=6379, db=0)

    def add_source(self, name):
        self.con.set("source:%s" % name, json.dumps({}))
        return {}

    def get_source(self, name):
        return json.loads(self.con.get("source:%s" % name))

    def delete_source(self, name):
        return self.con.delete("source:%s" % name)

    def get_thumbnails(self, name):
        metas = self.con.get("source:%s" % name)
        return [ImageMeta(name, meta.name, meta.size) for meta in json.loads(metas)]

    def get_thumbnail(self, source_name, size):
        try:
            metas = json.loads(self.con.get("source:%s" % source_name))
            meta = metas["%s_%s" % (source_name, size)]
            return ImageMeta(source_name, meta['name'], meta['size'])
        except KeyError:
            return None

    def add_thumbnail(self, source_name, size, name):
        meta = {
            'source_name': source_name,
            'name': name,
            'size': size
        }
        dict_metas = self.get_source(source_name)
        dict_metas[name] = meta
        self.con.set("source:%s" % name, json.dumps(dict_metas))
        return ImageMeta(source_name, name, size)

    def delete_thumbnail(self, source_name, size):
        name = "%s_%s" % (source_name, size)
        dict_metas = self.get_source(source_name)
        del dict_metas[name]
        self.con.set("source:%s" % name, json.dumps(dict_metas))
