import os
import shutil
import tempfile

from django.core.files.storage import FileSystemStorage

"""
Temporary Storage class for test. Copied from Smiley Chris' Easy Thumbnails test package
https://github.com/SmileyChris/easy-thumbnails/blob/master/easy_thumbnails/test.py
"""
class TemporaryStorage(FileSystemStorage):
    """
    A storage class useful for tests that uses a temporary location to store
    all files and provides a method to remove this location when it is finished
    with.
    """

    def __init__(self, *args, **kwargs):
        """
        Create the temporary location.
        """
        self.temporary_location = os.path.join(tempfile.gettempdir(), 'thumbs_test')
        
        super(TemporaryStorage, self).__init__(location=self.temporary_location, *args,
                                               **kwargs)

    def delete_temporary_storage(self):
        """
        Delete the temporary directory created during initialisation.
        This storage class should not be used again after this method is
        called.
        """
        temporary_location = getattr(self, 'temporary_location', None)
        if temporary_location:
            shutil.rmtree(temporary_location)

