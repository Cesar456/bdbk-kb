#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
import re
import time
import urllib2

from lxml import etree

proxy = urllib2.ProxyHandler({'http': '127.0.0.1:8123'})
opener = urllib2.build_opener(proxy)
urllib2.install_opener(opener)

def extract_categories(cat_url):
    time.sleep(1.0)
    print 'Downloading', cat_url
    data = urllib2.urlopen(cat_url).read()

    root = etree.HTML(data)

    sub_cats = []
    for node in root.findall('.//*[@id="mw-subcategories"]//*[@class="CategoryTreeItem"]'):
        a = node.find('.//a')
        cat_name = a.text
        cat_page_url = 'http://zh.wikipedia.org' + a.get('href')
        cat_stat_str = node.find('.//span[@dir="ltr"]').text
        cat_subcat_count = re.findall(ur'(\d+)个分类', cat_stat_str)
        cat_subpage_count = re.findall(ur'(\d+)个页面', cat_stat_str)
        cat_subcat_count = int(cat_subcat_count[0]) if len(cat_subcat_count) else 0
        cat_subpage_count = int(cat_subpage_count[0]) if len(cat_subpage_count) else 0

        print 'Processing %s, %d subcats, %d subpages' % (cat_name, cat_subcat_count, cat_subpage_count)

        sub_cats.append({
            'name': cat_name,
            'page_url': cat_page_url,
            'subcat_count': cat_subcat_count,
            'subpage_count': cat_subpage_count,
            'subcats': extract_categories(cat_page_url)
        })

    return sub_cats

if __name__ == '__main__':
    cats = extract_categories('http://zh.wikipedia.org/wiki/Category:%E9%A0%81%E9%9D%A2%E5%88%86%E9%A1%9E')
    print json.dumps(cats)
