"""
Django command to wait for the database to be available

"""
import time

from django.core.management.base import BaseCommand
from psycopg2 import OperationalError as Psycopg2Error
from django.db.utils import OperationalError


class Command(BaseCommand):
    """Django command to wait for database until available"""

    def handle(self, *args, **options):
        db_up = False

        self.stdout.write("Waiting for database...")
        while not db_up:
            try:
                self.check(databases=['default'])
                db_up = True
            except (Psycopg2Error, OperationalError):
                self.stdout.write("Database unavailable, waiting 1s...")
                time.sleep(1)

        self.stdout.write(self.style.SUCCESS("Database available!"))
