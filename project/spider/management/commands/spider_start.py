import scrapy
from django.conf import settings
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
                            help='download delay.')

        parser.add_argument('--proxy-list',
                            type=str,
                            default='',
                            help='proxy list.')

    def handle(self, *args, **options):
        setting = {
            'USER_AGENT': options['user_agent'],
            'DOWNLOAD_DELAY': options['download_delay'],
            'LOG_FILE': settings.SCRAPY_LOG_FILE,
            'LOG_LEVEL': settings.SCRAPY_LOG_LEVEL,
        }

        if options['proxy_list']:
            try:
                f = open(options['proxy_list'])
            except IOError as e:
                raise CommandError('cannot open proxy list file for read')

            # Retry many times since proxies often fail
            setting['RETRY_TIMES'] = 10
            # Retry on most error codes since proxies fail for different reasons
            setting['RETRY_HTTP_CODES'] = [500, 503, 504, 400, 403, 404, 408]
            setting['DOWNLOADER_MIDDLEWARES'] = {
                'scrapy.downloadermiddlewares.retry.RetryMiddleware': 90,
                'spider.randomproxy.RandomProxy': 100,
                'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 110,
            }
            setting['PROXY_LIST'] = options['proxy_list']

        process = CrawlerProcess(setting)

        process.crawl(BaiduSpider)
        process.start()
