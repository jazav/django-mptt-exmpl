# https://github.com/cod1sta/snippets/blob/master/blog/provide-initial-data-in-django-projects-like-django-fixtures-but-better-part-one/total_setup.py
from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand

PROJECT_USES_MULTISITES = False
try:
    from django.contrib.sites.models import Site

    PROJECT_USES_MULTISITES = True
except (ImportError, RuntimeError):
    pass

PROJECT_USES_CMS = False

try:
    from wagtail.core.models import Page, PageRevision
    from wagtail.core.models import Site as WagtailSite

    PROJECT_USES_CMS = True
except (ImportError, RuntimeError):
    pass


class Command(BaseCommand):
    """Sets up initial project data & settings. Also in production!"""

    help = "Sets up initial project data & settings. Also in production!"

    @staticmethod
    def _set_domain():
        """Sets the django and wagtail domains.

        Across all environments.
        """
        if PROJECT_USES_MULTISITES:
            current_site = Site.objects.get_current()
            if settings.DEBUG:
                current_site.domain = "localhost:8000"
                current_site.name = "localhost dev"
            elif getattr(settings, "STAGING", False):
                current_site.domain = f"test.{settings.DOMAIN}"
                current_site.name = f"test.{settings.DOMAIN}"
            else:
                current_site.domain = f"www.{settings.DOMAIN}"
                current_site.name = f"www.{settings.DOMAIN}"
            current_site.save()

            if PROJECT_USES_CMS:
                wagtail_site = WagtailSite.objects.get()
                wagtail_site.hostname = current_site.domain
                wagtail_site.site_name = current_site.name
                wagtail_site.save()

    def setup_production(self):
        """PRODUCTION ONLY STUFF."""
        self._set_domain()
        call_command("create_project_users", verbosity=self.verbosity)

    def setup_development(self):
        """DEVELOPMENT ONLY STUFF."""
        call_command("create_people", verbosity=self.verbosity)
        self.setup_production()

    def handle(self, *args, **options):
        """entry point"""
        self.verbosity = options["verbosity"]
        if not settings.DEBUG:
            if self.verbosity > 0:
                self.stdout.write("Setting up production defaults...")
            self.setup_production()
            return

        if self.verbosity > 0:
            self.stdout.write("Setting up sensible development defaults...")
        self.setup_development()
