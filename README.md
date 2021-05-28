[![Build
Status](https://travis-ci.org/ui/django-thumbnails.png?branch=master)](https://travis-ci.org/ui/django-thumbnails)

Design:

-   Uses Django Storage API
-   Uses flexible meta data store. Uses Redis as metadata store.
-   Supports creating thumbnails in different formats, for example from
    JPG to WEBP to reduce file size

Supported image formats:

-   JPG/JPEG
-   GIF
-   PNG
-   WEBP

## Installation

-   Add thumbnails to INSTALLED_APPS in settings.py.
-   Run python manage.py migrate to create database metadata backend.

## Usage

settings.py:

```python
THUMBNAILS = {
    'METADATA': {
        'BACKEND': 'thumbnails.backends.metadata.DatabaseBackend',
    },
    'STORAGE': {
        'BACKEND': 'django.core.files.storage.FileSystemStorage',
        # You can also use Amazon S3 or any other Django storage backends
    }
    'SIZES': {
        'small': {
            'PROCESSORS': [
                {'PATH': 'thumbnails.processors.resize', 'width': 10, 'height': 10},
                {'PATH': 'thumbnails.processors.crop', 'width': 80, 'height': 80}
            ],
            'POST_PROCESSORS': [
                {
                    'PATH': 'thumbnails.post_processors.optimize',
                    'png_command': 'optipng -force -o7 "%(filename)s"',
                    'jpg_command': 'jpegoptim -f --strip-all "%(filename)s"',
                },
            ],
        },
        'large': {
            'PROCESSORS': [
                {'PATH': 'thumbnails.processors.resize', 'width': 20, 'height': 20},
                {'PATH': 'thumbnails.processors.flip', 'direction': 'horizontal'}
            ],
        },
        'watermarked': {
            'PROCESSORS': [
                {'PATH': 'thumbnails.processors.resize', 'width': 20, 'height': 20},
                # Only supports PNG. File must be of the same size with thumbnail (20 x 20 in this case)
                {'PATH': 'thumbnails.processors.add_watermark', 'watermark_path': 'watermark.png'}
            ],
        }
    }
}
```

If you prefer to use Redis as your metadata storage backend (for performance reasons):

```python
THUMBNAILS = {
    'METADATA': {
        'PREFIX': 'thumbs',
        'BACKEND': 'thumbnails.backends.metadata.RedisBackend',
        'db': 2,
        'port': 6379,
        'host': 'localhost',
    },
}
```

## Image Processors

`django-thumbnails` comes with a few builtin image processors:

```python
    # To use the following processors, put the arguments of processors in SIZES definition
    thumbnails.processors.resize(width, height, method) ## `method` can be `stretch`, `fit` or `fill`
    thumbnails.processors.rotate(degrees)
    thumbnails.processors.flip(direction)
    thumbnails.processors.crop(width, height, center)
    thumbnails.processors.add_watermark(watermark_path)
```

Processors are applied sequentially in the same order of definition.


## Storage Backend

New in version 0.5.0 is per field, customizable storage backend. If you want specific fields to use
a different storage backend, you can specify it directly when declaring the field. e.g:

```python
class Food(models.Model):
    image = ImageField(storage=FileSystemStorage(), upload_to='food')
```

Storage that is specified on field will be used instead of storage that is specified in the settings.


In python:

```python
from thumbnails.fields import ImageField

class Food(models.Model):
    image = ImageField()


food = Food.objects.latest('id')
food.image.thumbnails.all()
food.image.thumbnails.small  # Generates "small" sized thumbnail
food.image.thumbnails.large  # Generates "large" sized thumbnail
food.image.thumbnails.small.url  # Returns "small" sized thumbnail URL
```

And here's how you'd use it in Django's template:

```python
{{ food.image.thumbnails.small.url }}  # Returns "small" sized thumbnail URL
```

Use resize_source_to to resize your image while saving it:

```python
from thumbnails.fields import ImageField

class Food(models.Model):
    image = ImageField(resize_source_to="medium")
```

Assuming medium is the size that you define in the settings. By passing
medium your saved image will be resized into medium's size

Use pregenerated_sizes to save your thumbnails into storage backend
while saving it:

```python
from thumbnails.fields import ImageField

class Food(models.Model):
    image = ImageField(pregenerated_sizes=["small", "large", "medium")
```

When deleting an image, you can opt to retain thumbnails by doing this:
``` python
banner.image.delete(with_thumbnails=False)
```


## Performance

If you need to fetch multiple thumbnails at once, use the provided `fetch_thumbnails` function
for better performance. `fetch_thumbnails` uses Redis pipeline to retrieve
thumbnail metadata in one go, avoiding multiple round trips to Redis.

```python
from thumbnails.field import fetch_thumbnails

food_a = Food.objects.get(id=1)
food_b = Food.objects.get(id=2)

fetch_thumbnails([food_a.image, food_b.image], ['small', 'large'])
```

This way, when we get thumbnails like thumbnail1.size_small or even
thumbnail1.all() we won't query to redis anymore. This feature is
currently only available for Redis metadata Backend.

## Management Commands

If you changed your size definition and want to regenerate the
thumbnails, use:

    python manage.py delete_thumbnails --model=app.Model --size=thumbnail_size_to_delete

## Running Tests

To run tests:

    `which django-admin.py` test thumbnails --settings=thumbnails.tests.settings --pythonpath=.

## Changelog

### Version 0.6.0 (2021-05-28)

* Added support for watermarking thumbnails. Thanks @marsha97!

### Version 0.5.0 (2021-05-1)

* You can now pass in `storage` kwarg into `ImageField` so you can specify different storage backends for different fields. Thanks @marsha97!
* Calling `image.delete(with_thumbnails=True)` will delete original image along with all thumbnails. Thanks @marsha97!

### Version 0.4.0 (2021-01-08)

-   Support for Django >= 3.0. Thanks @christianciu!
-   Added `pregenerated_sizes` to ImageField to allow thumbnails to be
    pregenerated on upload. Thanks @marsha97!
-   Thumbnails can be generated in different formats (e.g: JPG source
    image to WEBP thumbnail). Thanks @yosephbernandus!

### Version 0.3.2

-   Fixed another bug in `fetch_thumbnails()` bug. Thanks @marsha97!

### Version 0.3.1

-   Fixed `fetch_thumbnails()` bug. Thanks @marsha97!

### Version 0.3.0

-   Added `fetch_thumbnails()` command to fetch multiple thumbnail
    metadata from Redis. Thanks @marsha97!

### Version 0.2.2

-   Fixed `RedisBackend.get_thumbnail()` bug that may cause excessive
    trips to Redis. Thanks @marsha97!

### Version 0.2.1

-   Add support for Django 1.11, 2.0 and 2.1

### Version 0.2.0

-   Improves performance on fields that have a large number of
    thumbnails
-   Add support for Django 1.8, 1.9 and 1.10

### Version 0.1.3

-   Fixes deprecation warning in Django 1.8

### Version 0.1.2

-   Fixes deprecation warning in Django 1.8

### Version 0.1.1

-   Use
    [shortuuid](https://github.com/stochastic-technologies/shortuuid)
    instead of uuid4() to be more space efficient

### Version 0.1.0

-   First public release

As of February 2015, this library is suitable for production use and has
been used for more than a year in [Stamps](http://stamps.co.id), an
Indonesian based CRM/loyalty system.
