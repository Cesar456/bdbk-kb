#!/usr/bin/env python

import scrapy
from scrapy.crawler import CrawlerProcess

from spider.spider import BaiduSpider

process = CrawlerProcess({
    'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
    'DOWNLOAD_DELAY': 0.5
})

process.crawl(BaiduSpider)
process.start()
