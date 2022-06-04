import json

from django.core.management.base import BaseCommand
from django.db import transaction
from channel_apps.web.base.models import People

import logging
from . import utils

# django 1.6, 1.5 and 1.4 supports
try:
    atomic_decorator = transaction.atomic
except AttributeError:
    atomic_decorator = transaction.commit_on_success

logger = logging.getLogger(__name__)

USERS = [
    {
        "first_name": "Jason",
        "last_name": "Segel",
        "job_title": "Actor",
    },
    {
        "first_name": "André",
        "last_name": "Benjamin",
        "job_title": "Actor",
    },
    {
        "first_name": "Евгений",
        "last_name": "Стычкин",
        "job_title": "Actor",
    },
    {
        "first_name": "Ольга",
        "last_name": "Сутулова",
        "job_title": "Actor",
    },
    {
        "first_name": "Ксения",
        "last_name": "Раппопорт",
        "job_title": "Actor",
    },
]


class Command(BaseCommand):
    """Creates people.

    Just create a list of people and save them to the database.
    """

    help = "Creates people for blogs."


    @atomic_decorator
    def create_people(self, verbosity):
        json.load()
        for user_data in USERS:
            user_data = user_data.copy()

            first_name = user_data["first_name"]
            last_name = user_data["last_name"]
            img_path = f"{first_name}_{last_name}.jpeg"

            created = False
            if not People.objects.filter(first_name=first_name, last_name=last_name).exists():
                people = People.objects.create(**user_data)
                utils.set_image(
                    obj=people,
                    attr_name="image",
                    img_path=img_path,
                )
                created = True
            if verbosity > 0:
                self.stdout.write(
                    self.style.SUCCESS(
                        "People record {first_name} {last_name} {noun}".format(first_name=first_name,
                                                                               last_name=last_name,
                                                                               noun="created" if created else "exists")))

    def handle(self, *args, **options):
        verbosity = options["verbosity"]
        self.create_people(verbosity)
