from django.core.management.base import BaseCommand
from graph import update as u

class Command(BaseCommand):
    help = 'Updates the database from multiple sources'

    def handle(self, *args, **kwargs):
        self.stdout.write("Checking for new case data from PHE to download")
        u.update()
        


