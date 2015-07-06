#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
import urllib2
from StringIO import StringIO

from lxml import etree


#proxy = urllib2.ProxyHandler({'http': '127.0.0.1:8123'})
#opener = urllib2.build_opener(proxy)
#urllib2.install_opener(opener)

def extract_hidden_cats():
    def extract_one_page(page_url):
        data = urllib2.urlopen(page_url).read()
        parser = etree.HTMLParser()
        tree = etree.parse(StringIO(data), parser)
        result = []
        for i in tree.xpath('//a[contains(@class, "CategoryTreeLabel")]'):
            result.append({
                'title': i.text,
                'url': i.get('href')
            })

        next_page_url = None
        for i in tree.xpath('//a'):
            if i.text and u'下一页' in i.text:
                next_page_url = 'https://zh.wikipedia.org/' + i.get('href')

        print len(result), 'pages, following:', next_page_url
        return result, next_page_url

    result, next_page_url = extract_one_page('https://zh.wikipedia.org/w/index.php?title=Category:%E9%9A%90%E8%97%8F%E5%88%86%E7%B1%BB')
    while next_page_url:
        nr, next_page_url = extract_one_page(next_page_url)
        result += nr

    return result


print json.dumps(extract_hidden_cats())
