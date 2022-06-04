import random
from django.apps import apps
from pathlib import Path
import logging
from django.contrib.contenttypes.models import ContentType
from django.core.files import File
from django.core.management.base import BaseCommand
from wagtail.core.models import Page
from wagtail.images.models import Image
from django.conf import settings
from wagtail.models import Locale
from wagtail_localize.models import LocaleSynchronization
from channel_apps.web.base.models import People
from django.utils.translation import gettext_lazy as _
from channel_apps.web.blog.models import BlogIndexPage, BlogPage, BlogPeopleRelationship

PROJECT_USES_MULTISITES = False
try:
    from django.contrib.sites.models import Site as DjangoSite

    PROJECT_USES_MULTISITES = True
except (ImportError, RuntimeError):
    pass

PROJECT_USES_WAGTAILMENUS = False
try:
    from wagtailmenus.conf import settings as wagtailmenu_settings

    PROJECT_USES_WAGTAILMENUS = True
except (ImportError, RuntimeError):
    pass

from channel_apps.web.home.models import (
    HomePage, FormPage,
)

from channel_apps.web.catalog.models import (
    UnitPage,
    UnitsIndexPage,
)

logger = logging.getLogger(__name__)

APP_DIR = Path(__file__).resolve().parent.parent.parent
FIXTURES_DIR = APP_DIR.joinpath("fixtures")

LOCALE_CODES = [a_tuple[0] for a_tuple in settings.LANGUAGES]
PRIMARY_LOCALE = settings.LANGUAGE_CODE


class Command(BaseCommand):
    """
    this command is used to create the initial wagtail cms page tree
    """

    help = "creates initial wagtail cms page tree"
    requires_system_checks = False

    def _setup(self):
        self._setup_locale()
        self._setup_home()
        self._setup_product_index_page()
        self._setup_product_page()
        self._setup_blog_index_page()
        self._setup_blog_page()
        self._setup_form_page()
        # This must be the last one
        self._setup_site()

    @staticmethod
    def _setup_locale():
        """Creates the locales."""
        locale_objects = []
        locale_manager = Locale.objects
        locale_class = locale_manager.model

        for locale_code in LOCALE_CODES:
            if not Locale.objects.filter(language_code=locale_code).exists():
                locale_objects.append(locale_class(language_code=locale_code))

        if len(locale_objects) > 0:
            Locale.objects.bulk_create(locale_objects)
            logger.debug("Locales created: %s", locale_objects)

        if not LocaleSynchronization.objects.exists():
            locale_from = Locale.objects.get(language_code=PRIMARY_LOCALE)
            locale_objects = Locale.objects.filter(language_code__in=LOCALE_CODES).exclude(language_code=PRIMARY_LOCALE)
            for locale in locale_objects:
                LocaleSynchronization.objects.create(sync_from=locale_from, locale=locale)

    @staticmethod
    def _setup_home():
        """Creates the language specific home pages."""
        # parent_page = LanguageRedirectionPage.objects.first()
        root = Page.get_first_root_node()
        homepage_content_type = ContentType.objects.get_for_model(HomePage)
        # For each supported language, create a new homepage
        locales = Locale.objects.all()
        for locale in locales:
            language_code: str = getattr(locale, 'language_code')
            locale_id: int = getattr(locale, 'id')

            if language_code is not None and language_code == PRIMARY_LOCALE:
                title = f"Home {language_code.upper()}"
                if language_code == "ru":
                    hero_text = "Компания BuyPremium"
                    seo_title = "Скидки Товары Продукты"
                    live = True
                elif language_code == "en":
                    hero_text = "We are BuyPremium."
                    seo_title = "Discounts Products Goods"
                    live = True
                else:
                    raise RuntimeError(f"unsupported language encountered: {language_code}")
                title = _(f"Home Page {PRIMARY_LOCALE.upper()}")
                homepage = HomePage(
                    title=title,
                    draft_title=title,
                    slug="home-page",
                    hero_text=_("We are BuyPremium."),
                    seo_title=seo_title,
                    show_in_menus=False,
                    live=live,
                    locale_id=locale_id,
                    content_type=homepage_content_type,
                )

                root.add_child(instance=homepage)
                homepage.save_revision().publish()

    @staticmethod
    def _setup_product_index_page():
        try:
            # Get primary Product Index Page
            primary_locale = Locale.objects.get(language_code=PRIMARY_LOCALE)

            page_content_type = ContentType.objects.get_for_model(UnitsIndexPage)
            title = _(f"Product Index {PRIMARY_LOCALE.upper()}")
            page = UnitsIndexPage(
                title=title,
                introduction=title,
                slug="units-index",
                show_in_menus=True,
                live=True,
                locale_id=primary_locale.id,
                content_type=page_content_type,
            )

            parent_page = HomePage.objects.get(locale_id=primary_locale.id)
            parent_page.add_child(instance=page)
            page.save_revision().publish()

            logger.debug("Default page created: %s", page)

        except HomePage.DoesNotExist:
            raise Exception("Parent page for {page} not found")

    @staticmethod
    def _setup_product_page():
        try:
            # Get primary Product Page
            primary_locale = Locale.objects.get(language_code=PRIMARY_LOCALE)

            page_content_type = ContentType.objects.get_for_model(UnitPage)
            page = UnitPage(
                title=_(f"Product Page {PRIMARY_LOCALE.upper()}"),
                introduction=_(f"Product Page {PRIMARY_LOCALE.upper()}"),
                slug=f"product",
                show_in_menus=False,
                live=True,
                locale_id=primary_locale.id,
                content_type=page_content_type,
            )

            parent_page = UnitsIndexPage.objects.get(locale_id=primary_locale.id)
            parent_page.add_child(instance=page)
            page.save_revision().publish()

            logger.debug("Default page created: %s", page)

        except UnitsIndexPage.DoesNotExist:
            raise Exception("Parent page for {page} not found")

    @staticmethod
    def _setup_blog_index_page():
        try:
            # Get primary Blog Index Page
            primary_locale = Locale.objects.get(language_code=PRIMARY_LOCALE)

            page_content_type = ContentType.objects.get_for_model(BlogIndexPage)
            title = _(f"Blog Index {PRIMARY_LOCALE.upper()}")
            page = BlogIndexPage(
                title=title,
                introduction=title,
                slug="blog-index",
                show_in_menus=True,
                live=True,
                locale_id=primary_locale.id,
                content_type=page_content_type,
            )

            parent_page = HomePage.objects.get(locale_id=primary_locale.id)
            parent_page.add_child(instance=page)
            page.save_revision().publish()

            logger.debug("Default page created: %s", page)

        except HomePage.DoesNotExist:
            raise Exception("Parent page for {page} not found")

    @staticmethod
    def _add_author_to_blog(blog_page):
        people_count = People.objects.count()
        if people_count > 0:
            author = People.objects.get(id=random.randint(1, people_count))
            BlogPeopleRelationship.objects.create(page=blog_page, people=author)
            logger.debug(f"Author {author} added to {blog_page}")

    @staticmethod
    def _setup_blog_page():
        try:
            # Get 4 Blog Pages
            primary_locale = Locale.objects.get(language_code=PRIMARY_LOCALE)

            page_content_type = ContentType.objects.get_for_model(BlogPage)
            parent_page = BlogIndexPage.objects.get(locale_id=primary_locale.id)
            title = _(f"Blog Page {PRIMARY_LOCALE.upper()}")
            for i in range(1, 4):
                page = BlogPage(
                    title=title,
                    introduction=title,
                    subtitle=title,
                    date_published="2022-03-01",
                    tags=_(f"Dress"),
                    slug=f"blog-page-{i}",
                    show_in_menus=False,
                    live=True,
                    locale_id=primary_locale.id,
                    content_type=page_content_type,
                )

                parent_page.add_child(instance=page)
                page.save_revision().publish()
                # Add author to blog
                Command._add_author_to_blog(page)
                logger.debug("Default page created: %s", page)

        except BlogIndexPage.DoesNotExist:
            raise Exception("Parent page for {page} not found")

    @staticmethod
    def _setup_form_page():
        try:
            # Get primary Form Page
            primary_locale = Locale.objects.get(language_code=PRIMARY_LOCALE)

            page_content_type = ContentType.objects.get_for_model(FormPage)
            title = _(f"Form Page {PRIMARY_LOCALE.upper()}")
            page = FormPage(
                title=title,
                intro=title,
                subtitle=title,
                slug="form-page",
                show_in_menus=True,
                live=True,
                locale_id=primary_locale.id,
                content_type=page_content_type,
                contact_text=_(f"Contact Page {PRIMARY_LOCALE.upper()}"),
                thank_you_text=_(f"Thank You Page {PRIMARY_LOCALE.upper()}"),
                email=f"{PRIMARY_LOCALE.upper()}@example.com",
                # phone={+79211111111},
            )

            parent_page = HomePage.objects.get(locale_id=primary_locale.id)
            parent_page.add_child(instance=page)
            page.save_revision().publish()

            logger.debug("Default page created: %s", page)

        except HomePage.DoesNotExist:
            raise Exception("Parent page for {page} not found")

    @staticmethod
    def _setup_site():
        # Note: this is wagtail's Site model, not django's.
        try:
            # Get primary HomePage (all others are created in from this one)
            primary_locale = Locale.objects.get(language_code=PRIMARY_LOCALE)
            root_page = HomePage.objects.get(locale_id=primary_locale.id)

            site_model = apps.get_model("wagtailcore.Site")
            if site_model.objects.filter(is_default_site=True).exists():

                site = site_model.objects.filter(is_default_site=True).first()
                site.root_page = root_page
                site_name = getattr(site, 'site_name', None)
                if site_name is None or site_name == '':
                    site.site_name = settings.DOMAIN_NAME
                site.save()
            else:
                site_model.objects.create(
                    hostname=settings.DOMAIN_NAME,
                    root_page=root_page,
                    is_default_site=True,
                    site_name=settings.DOMAIN_NAME,
                )
            logger.debug("Site created or updated")

            # Delete the default homepage created by wagtail migrations If migration is run
            # multiple times, it may have already been deleted
            try:
                # default_home = Page.objects.filter(title="Welcome to your new Wagtail site!")[0]
                # default_home.delete()
                Page.objects.filter(id=2).delete()
            except:
                pass

            logger.debug("Default HomePage deleted")

        except HomePage.DoesNotExist:
            raise Exception("No root page found")

    @staticmethod
    def _set_image(instance, attr_name, folder_path, img_path):
        """Helper to set images on models."""
        img_path = folder_path.joinpath(img_path)
        # Create and set the file if it does not yet exist.
        qs = Image.objects.filter(title=img_path.name)
        if not qs.exists():
            with open(img_path, "rb") as f:
                # setting name= is important. otherwise it uses the entire file path as
                # name, which leaks server filesystem structure to the outside.
                image_file = File(f, name=img_path.stem)
                image = Image(title=img_path.name, file=image_file.open())
                image.save()
        else:
            image = qs[0]
        setattr(instance, attr_name, image)
        instance.save()

    def handle(self, raise_error=False, *args, **options):
        # Root Page and a default homepage are created by wagtail migrations so check
        # for > 2 here
        verbosity = options["verbosity"]
        checks = [Page.objects.all().count() > 2]
        if any(checks):
            # YOU SHOULD NEVER RUN THIS COMMAND WITHOUT PRIOR DB DUMP
            raise RuntimeError("Pages exists. Aborting.")

        self._setup()
        if verbosity > 0:
            msg = "Page Tree successfully created."
            self.stdout.write(self.style.SUCCESS(msg))
