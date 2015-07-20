import scrapy
from django.core.management.base import BaseCommand, CommandError
from scrapy.crawler import CrawlerProcess

from spider.spider import BaiduSpider


class Command(BaseCommand):
    help = 'start the spider'

    def add_arguments(self, parser):
        parser.add_argument('--user-agent',
                            type=str,
                            default='Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
                            help='user agent for this spider.')

        parser.add_argument('--download-delay',
                            type=float,
                            default=0.5,
                            help='host of mongo db server.')

    def handle(self, *args, **options):
        process = CrawlerProcess({
            'USER_AGENT': options['user_agent'],
            'DOWNLOAD_DELAY': options['download_delay']
        })

        process.crawl(BaiduSpider)
        process.start()
