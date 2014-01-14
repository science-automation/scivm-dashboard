from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from optparse import make_option

class Command(BaseCommand):
    help = 'Creates missing API keys for users'

    def handle(self, *args, **options):
        from apikey.models import ApiKey
        users = User.objects.filter(apikey__isnull=True)
        for user in users:
            print('Creating API key for {}'.format(user.username))
            k = ApiKey()
            k.user = user
            k.save()
