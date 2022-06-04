import os

from django.conf import settings
from django.core.files.storage import default_storage, FileSystemStorage
from django.core.management.base import BaseCommand
from django.core.management import call_command

from wagtail.core.models import Site, Page


class Command(BaseCommand):
    help = 'Load initial data'

    def _copy_files(self, local_storage, path):
        """
        Recursively copy files from local_storage to default_storage. Used
        to automatically bootstrap the media directory (both locally and on
        cloud providers) with the images linked from the initial data (and
        included in MEDIA_ROOT).
        """
        directories, file_names = local_storage.listdir(path)
        for directory in directories:
            self._copy_files(local_storage, path + directory + '/')
        for file_name in file_names:
            with local_storage.open(path + file_name) as file_:
                default_storage.save(path + file_name, file_)

    def handle(self, **options):
        commands_dir = os.path.join(settings.PROJECT_DIR, 'home', 'fixtures')
        commands_file = os.path.join(commands_dir, 'ecom_dev.json')

        print("Copying media files to configured storage...")

        local_storage = FileSystemStorage(os.path.join(commands_dir, 'media'))
        self._copy_files(local_storage, '')  # file storage paths are relative

        # Wagtail creates default Site and Page instances during install, but we already have
        # them in the data load. Remove the auto-generated ones.
        if Site.objects.filter(hostname='localhost').exists():
            Site.objects.get(hostname='localhost').delete()
        if Page.objects.filter(title='Welcome to your new Wagtail site!').exists():
            Page.objects.get(title='Welcome to your new Wagtail site!').delete()

        call_command('loaddata', commands_file, verbosity=0)

        self.stdout.write(
            self.style.SUCCESS("Awesome. Your data is loaded!"))
