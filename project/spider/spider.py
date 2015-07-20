import datetime
import logging
import re
import zlib

import pymongo
import scrapy
from bson import binary as pymongo_binary

from project import setup_database
from django.conf import settings
from django.utils import timezone

from bdbk.models import NamedEntity

from .models import SpiderEntry


class BaiduSpider(scrapy.Spider):
    name = 'bdbk_spider'

    def start_requests(self):
        entrys = SpiderEntry.getEntryForDownload(1)
        mongodb_settings = settings.BDBK_SETTINGS['page_source_mongodb']
        self.mongodb = pymongo.MongoClient(mongodb_settings['host'], mongodb_settings['port'])

        for entry in entrys:
            yield scrapy.Request(entry.url, callback=self.handle_page, meta={'dbo': entry})

    def handle_page(self, response):
        logger = logging.getLogger('spider.handler')
        entry = response.request.meta['dbo']
        if entry.mongodb_id:
            self.mongodb.baidu.data.delete_one({'_id': entry.mongodb_id})

        updatetime = timezone.make_aware(datetime.datetime.now())

        try:
            NamedEntity.updateFromPage(response.url, response.body, updatetime)
        except Exception as e:
            logger.exception(e)
            logger.error('failed to update page: %s', response.url)

        newid = self.mongodb.baidu.data.insert({
            'url': response.request.url,
            'actualurl': response.url,
            'content': pymongo_binary.Binary(zlib.compress(response.body, 9)),
            'lastmodifytime': updatetime.strftime('%Y-%m-%d %H:%M:%S'),
        })

        entry.mongodb_id = newid
        entry.actual_url = response.url
        entry.last_modified = updatetime
        entry.save()

        for link in response.xpath('//a/@href').extract():
            url = response.urljoin(link)
            regx_match = re.search(r'(http://baike\.baidu\.com/(subview|view)/.*?)(#|$)', link)
            if regx_match:
                new_entry, created = SpiderEntry.objects.get_or_create(url=regx_match.group(1))
                if created:
                    yield scrapy.Request(new_entry.url, callback=self.handle_page, meta={'dbo': new_entry})
