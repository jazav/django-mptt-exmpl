from wagtail.images.models import Rendition
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Delete all renditions'

    def handle(self, **options):
        print("Deleting renditions...")
        Rendition.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('Successfully deleted all renditions'))
