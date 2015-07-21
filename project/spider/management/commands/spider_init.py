import scrapy
from django.core.management.base import BaseCommand, CommandError

from spider.models import SpiderEntry


class Command(BaseCommand):
    help = 'init the spider with http://baike.baidu.com/view/1.htm'

    def handle(self, *args, **options):
        SpiderEntry.objects.get_or_create(url='http://baike.baidu.com/view/1.htm')
