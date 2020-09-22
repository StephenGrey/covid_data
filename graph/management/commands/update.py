from django.core.management.base import BaseCommand
from graph import update as u
import logging

class Command(BaseCommand):
    help = 'Updates the database from multiple sources'

    def handle(self, *args, **kwargs):
        try:
            self.stdout.write("Updating all data from APIs")
            u.update()
        except Exception as e:
            self.stdout("Error")
            self.stdout.write(e)


