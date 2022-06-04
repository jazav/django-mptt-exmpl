from django.core.management import execute_from_command_line
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Run Django shell'

    def handle(self, **options):
        execute_from_command_line(["manage.py", "shell"])
        self.stdout.write(self.style.SUCCESS('Successfully exited from Django shell'))
