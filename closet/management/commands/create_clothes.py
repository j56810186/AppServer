
from pathlib import Path

from django.core.management.base import BaseCommand
from django.db import transaction

from closet.models import Clothe, User

FILENAME_TO_TYPE_DICT = {
    'shirt': 1,
    'tshirt': 2,
    'pants': 3,
    'shorts': 4,
    'skirt': 5,
    'dress': 6,
    'shoes': 7,
}

class Command(BaseCommand):
    help = 'Create clothes.'

    def add_arguments(self, parser):
        parser.add_argument('path', type=str)

    @transaction.atomic
    def handle(self, *args, **options):
        root_path = options['path']
        for idx, path in enumerate(Path(root_path).iterdir()):
            if path.is_dir() and 'user' in str(path):
                user = User.objects.filter(id=idx)
                for imgp in Path(path).iterdir(): # image path
                    stem = imgp.stem
                    stem_splitted = stem.split('_')
                    if len(stem_splitted) == 2:
                        type = stem_splitted[-1][:-1] # do not select the last char, which is just a number, not type.
                        type = FILENAME_TO_TYPE_DICT[type]
                        Clothe.objects.create(
                            user=user,
                            name=stem,

                        )


        self.stdout.write(self.style.SUCCESS(f'Successfully create clothes.'))
