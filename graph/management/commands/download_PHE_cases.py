from django.core.management.base import BaseCommand
from graph import phe_fetch as pf

class Command(BaseCommand):
    help = 'Downloads the latest PHE cases data'

    def handle(self, *args, **kwargs):
        self.stdout.write("Checking for new case data from PHE to download")
        pf.check_and_download()
        


