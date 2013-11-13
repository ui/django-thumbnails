from django.conf import settings

THUMBNAILS = getattr(settings, 'THUMBNAILS', {})

SIZES = THUMBNAILS.get('SIZES', None)
