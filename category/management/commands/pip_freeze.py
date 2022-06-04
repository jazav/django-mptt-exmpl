from django.core.management.base import BaseCommand
import sys
import platform

if sys.version_info >= (3, 8):
    from importlib import metadata as importlib_metadata
else:
    import importlib_metadata


class Command(BaseCommand):
    help = 'Show all installed packages'

    def handle(self, **options):
        print("\nPlatform:")
        print(f"{platform.system()} {platform.version()} {platform.release()}")
        print("\nPython version:")
        print(f"{sys.version}")
        print("\nPackages:")

        dists = importlib_metadata.distributions()
        sorted_dists = sorted((dist for dist in dists), key=lambda x: x.metadata["Name"].lower())
        for dist in sorted_dists:
            name = dist.metadata["Name"]
            version = dist.version
            # dist_license = dist.metadata["License"]
            print(f'{name}=={version}')

        self.stdout.write(self.style.SUCCESS('Successfully showed all packages'))
