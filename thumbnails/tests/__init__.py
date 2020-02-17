from django.conf import settings

REDIS_BACKEND = settings.THUMBNAILS
REDIS_BACKEND["METADATA"] = {
    'BACKEND': 'thumbnails.backends.metadata.RedisBackend'
}
