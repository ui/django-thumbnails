from django.test import TestCase
from django.core.files import File
from django.core.management import call_command

from .models import TestModel
from thumbnails.backends import metadata


class CommandTest(TestCase):

    def test_delete_thumbnails(self):
        metadata_backend = metadata.get_backend()
        get_thumbnail = metadata_backend.get_thumbnail
        instance = TestModel.objects.create()

        with open('thumbnails/tests/tests.png', 'rb') as image_file:
            instance.avatar = File(image_file)
            instance.save()

        with open('thumbnails/tests/tests.png', 'rb') as image_file:
            instance.profile_picture = File(image_file)
            instance.save()

        instance = TestModel.objects.get(id=instance.id)
        instance.avatar.thumbnails.create(size='small')
        instance.avatar.thumbnails.create(size='large')
        instance.profile_picture.thumbnails.create(size='small')
        instance.profile_picture.thumbnails.create(size='large')

        self.assertTrue(get_thumbnail(instance.avatar.name, 'small'))
        self.assertTrue(get_thumbnail(instance.avatar.name, 'large'))
        self.assertTrue(get_thumbnail(instance.profile_picture.name, 'small'))
        self.assertTrue(get_thumbnail(instance.profile_picture.name, 'large'))

        call_command('delete_thumbnails', path_to_model='tests.TestModel',
                     field_name='avatar', size='small')

        # Ensure only the relevant thumbnails are deleted
        self.assertFalse(get_thumbnail(instance.avatar.name, 'small'))
        self.assertTrue(get_thumbnail(instance.avatar.name, 'large'))
        self.assertTrue(get_thumbnail(instance.profile_picture.name, 'small'))
        self.assertTrue(get_thumbnail(instance.profile_picture.name, 'large'))
