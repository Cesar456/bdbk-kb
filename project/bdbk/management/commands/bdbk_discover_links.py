from django.core.management.base import BaseCommand, CommandError

from bdbk.linkbuilder import *


class Command(BaseCommand):
    help = 'discover new links within bdbk tuples.'

    def add_arguments(self, parser):
        parser.add_argument('--class', required=True, type=str, help='LinkBuilder class to use.')

    def handle(self, *args, **options):
        cls = globals().get(options['class'], None)

        if not cls:
            print 'Class', options['class'], 'not found.'
            return

        cls().find_links()
