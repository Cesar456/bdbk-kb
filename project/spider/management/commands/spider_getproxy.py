import urllib2

from lxml import etree

from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'get a new list of proxies'

    def handle(self, *args, **options):
        net = urllib2.urlopen('http://cn-proxy.com/')
        page = etree.parse(net, etree.HTMLParser())

        for i in page.xpath('//div[@class="table-container"]'):
            rows = list(i.xpath('.//tbody/tr'))[:10]
            for row in rows:
                print 'http://%s:%s/' % (row.xpath('.//td[1]/text()')[0], row.xpath('.//td[2]/text()')[0])
