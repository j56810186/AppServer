
from pathlib import Path

from django.core.management.base import BaseCommand
from closet.models import Clothe

class Command(BaseCommand):
    help = 'Create clothes.'

    def add_arguments(self, parser):
        parser.add_argument('path', type=str)

    def handle(self, *args, **options):
        root_path = options['path']
        for path in Path(root_path).iterdir():
            assert path.is_dir()
        # self.stdout.write(self.style.SUCCESS(f'Successfully create user: {username}'))
