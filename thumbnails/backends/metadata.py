import os
from thumbnails.models import Source, ThumbnailMeta
from thumbnails.conf import settings
from django.core.exceptions import ImproperlyConfigured

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
        return ThumbnailMeta.objects.filter(source__name=name)

    def get_thumbnail(self, source_name, size):
        try:
            return ThumbnailMeta.objects.get(source__name=source_name, size=size)
        except ThumbnailMeta.DoesNotExist:
            return None

    def add_thumbnail(self, source_name, size, name):
        source = self.get_source(source_name)

        if not settings.SIZES:
            raise ImproperlyConfigured("Cannot find THUMBNAIL SIZES in settings.")

        size_desc = settings.SIZES.get(size, None)
        if not size_desc:
            raise ImproperlyConfigured("Cannot find %s in settings." % size)
        else:
            filename, extension = os.path.splitext(name)
            name = "%s_%s%s" % (filename, size, extension)

        return ThumbnailMeta.objects.create(source=source, size=size, name=name)

    def delete_thumbnail(self, source_name, size):
        ThumbnailMeta.objects.filter(source__name=source_name, size=size).delete()
