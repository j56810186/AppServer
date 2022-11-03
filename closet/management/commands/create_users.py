
from django.core.management.base import BaseCommand
from closet.models import User

class Command(BaseCommand):
    help = 'Create users.'

    def add_arguments(self, parser):
        parser.add_argument('usernames', nargs='+', type=str)

    def handle(self, *args, **options):
        for username in options['usernames']:
            user = User.objects.create_user(
                username=username,
                name=username,
                email=f'{username}@test.testsite',
                phone='0900000000',
                password='adminadmin',
            )
            self.stdout.write(self.style.SUCCESS(f'Successfully create user: {username}'))
