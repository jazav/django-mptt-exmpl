# https://github.com/cod1sta/snippets/blob/master/blog/provide-initial-data-in-django-projects-like-django-fixtures-but-better-part-one/create_project_users.py
import django.contrib.auth.models
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.template.loader import render_to_string
from django.db import transaction


# django 1.6, 1.5 and 1.4 supports
try:
    atomic_decorator = transaction.atomic
except AttributeError:
    atomic_decorator = transaction.commit_on_success

PROJECT_USES_MULTISITES = False
try:
    from django.contrib.sites.models import Site

    PROJECT_USES_MULTISITES = True
except (ImportError, RuntimeError):
    pass

user_model = get_user_model()
# some random team members generated via https://uinames.com/
USERS = [
    {
        "username": "admin",
        "password": "admin",
        "email": "lisa_fox@example.com",
        "first_name": "Lisa",
        "last_name": "Fox",
    },
]


class Command(BaseCommand):
    """Creates project users.

    In development we simply set ``admin`` as password. In production we create users
    without valid passwords, so we can simply do a password reset procedure.
    """

    help = "Creates project users."
    requires_system_checks = False

    @staticmethod
    def send_activation_email(self, user, site=None):
        """
        Send an activation email to the ``user``.
        The activation email will make use of two templates:

        ``activation_email_subject.txt``
        This template will be used for the subject line of the
        email. Because it is used as the subject line of an email,
        this template's output **must** be only a single line of
        text; output longer than one line will be forcibly joined
        into only a single line.

        ``activation_email.txt``
        This template will be used for the body of the email.

        These templates will each receive the following context
        variables:

        ``activation_key``
        The activation key for the new account.

        ``expiration_days``
        The number of days remaining during which the account may
        be activated.

        ``site``
        An object representing the site on which the user
        registered; depending on whether ``django.contrib.sites``
        is installed, this may be an instance of either
        ``django.contrib.sites.models.Site`` (if the sites
        application is installed) or
        ``django.contrib.sites.models.RequestSite`` (if
        not). Consult the documentation for the Django sites
        framework for details regarding these objects' interfaces.

        """
        ctx_dict = {'activation_key': user.api_registration_profile.activation_key,
                    'expiration_days': settings.REGISTRATION_API_ACCOUNT_ACTIVATION_DAYS,
                    'site': site}
        subject = render_to_string('activation_email_subject.txt',
                                   ctx_dict)
        # Email subject *must not* contain newlines
        subject = ''.join(subject.splitlines())
        message = render_to_string('activation_email.txt',
                                   ctx_dict)
        user.email_user(subject, message, settings.DEFAULT_FROM_EMAIL)

    @atomic_decorator
    def create_inactive_user(self, username=None, email=None, password=None):

        if username is not None:
            new_user = user_model.objects.create_user(username, email, password)
        else:
            new_user = user_model.objects.create_user(email=email, password=password)
        new_user.is_active = False
        new_user.save()
        # create_profile(new_user)

        site = None
        if PROJECT_USES_MULTISITES:
            site = Site.objects.get_current()

        self.send_activation_email(new_user, site)
        return new_user

    def handle(self, *args, **options):
        verbosity = options["verbosity"]

        # Uncomment to create default admin user
        # admin_created = False
        # if not user_model.objects.filter(email="admin@simpleloop.com").exists():
        #     self.create_inactive_user(username="", email=settings.ADMIN_EMAIL, password="admin")
        #     admin_created = True
        # if verbosity > 0:
        #     self.stdout.write(self.style.SUCCESS("Admin created" if admin_created else "Admin exists."))

        for user_data in USERS:
            user_data = user_data.copy()

            username = user_data["username"]
            created = False
            created_user = None
            if not user_model.objects.filter(username=username).exists():
                created_user = user_model.objects.create_superuser(**user_data)
                created = True
            if verbosity > 0:
                self.stdout.write(
                    self.style.SUCCESS("User {username} {noun}".format(username=username, noun="created" if created else "exists")))
            #  When we run in production, make sure this command doesnt set "admin" as
            #  valid password lol.
            if not settings.DEBUG and created_user:
                # By using unusable password we get superusers which can then reset
                # their password.
                created_user.set_unusable_password()
                created_user.save()
                if verbosity > 0:
                    self.stdout.write(self.style.ERROR("\tProduction run: set invalid password."))
