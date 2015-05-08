#!/usr/bin/python
# -*- coding: utf8 -*-
# This script reads baidu baike data, and parses its infobox, produces
# tuples of the name entities

from scrapy.http import TextResponse
import re
import os
import gzip
import sys
import logging
from process_relations import cleanup_verb

class Extractor(object):
    link_regx = re.compile(r'href=["\']*([^"\']+)["\']*')
    lemma_list_link = re.compile(r'<a.*?href=["\']*([^"\']+)["\']*.*?>(.*?)</a>')

    def __init__(self):
        pass

    def get_tuples(self, html):
        '''Handles a real page, returns its tuple list
        '''
        tuples = []

        page_biitems = html.xpath("//*[@class='biItem']")
        for i in page_biitems:
            page_bititle = i.xpath(".//*[@class='biTitle']//text()").extract()
            if len(page_bititle) == 0:
                continue

            bititle = re.sub(r'[\xa0\s]', '', ''.join(page_bititle))
            bititle = cleanup_verb(bititle)
            if not bititle:
                continue

            # if we have a <br>, then multiple bicontents should be produced
            page_bicontents = i.xpath(".//*[@class='biContent']//text()|.//a").extract()
            target = ''

            in_href=False
            for bicontent in page_bicontents:
                if '<a' in bicontent:
                    if in_href:
                        target += '}}'

                    mch = re.search(self.link_regx, bicontent)
                    if mch:
                        in_href = True
                        target += '{{link:%s|' % mch.group(1)
                else:
                    if '\n' in bicontent:
                        target += re.sub(r'[\xa0\s\n]', '', bicontent)
                        if target:
                            tuples.append((bititle, target))
                        target = ''
                    else:
                        target += bicontent.strip()

                    if in_href:
                        in_href = False
                        target += '}}'

            tuples.append((bititle, target))

        return tuples

    def get_title(self, html):
        # page title
        page_title = html.xpath("//head//title//text()").extract()
        if len(page_title) == 1 and u'_百度百科' in page_title[0]:
            page_title = page_title[0]
            page_title = page_title[:page_title.rfind('_')]

            return page_title
        else:
            # logging.warning('Unable to extract title: page_id(%d)', page_id)
            return None

    def get_search_term(self, html):
        # search term
        search_term = html.xpath("//input[@id='topword']//@value").extract()
        if len(search_term) == 1:
            return search_term[0]
        else:
            return None

    def get_abstract(self, html):
        # abstract
        page_abstract = html.xpath("//head//meta[@name='Description']//@content").extract()
        if len(page_abstract) == 1:
            return page_abstract[0]
        else:
            return None

    def get_lemma_list(self, html):
        lemmas = html.xpath("//div[@id='lemma-list']//ul//a").extract()
        result = []
        for i in lemmas:
            mch = re.search(self.lemma_list_link, i)
            if mch:
                result.append('{{link:%s|%s}}' % (mch.group(1), mch.group(2)))
        return result

    def extract(self, page_id, content):
        # scrapy doc says it will detect encoding, but we should really
        # be careful at that
        page = TextResponse(
            "file:///", 
            headers={}, 
            status=200, 
            body=content)

        title = self.get_title(page)
        search_term = self.get_search_term(page)

        if search_term:
            abstract = self.get_abstract(page)
            tuples = self.get_tuples(page)

            print 'A real page'
            print title, search_term
            print abstract
            for i in tuples:
                print '\t'.join(i)
        else:
            lemmas = self.get_lemma_list(page)

            print 'A lemma list'
            print title
            print ';'.join(lemmas)

extractor = Extractor()

if __name__ == '__main__':
    import argparse
    from baidu_database import BaiduDatabase

    parser = argparse.ArgumentParser(
        description='I will read baidu baike and produce you the info tuples of its infobox.')
    parser.add_argument('--dir', required=True, help='database dir.')
    parser.add_argument('--db-name', help='name of the database.')
    parser.add_argument('--log', required=True, help='log file name.')

    args = parser.parse_args()
    dir = args.dir
    db_name = args.db_name
    log_fn = args.log

    logging.info('Source: %s in %s', db_name, dir)

    db = BaiduDatabase(dir, db_name)
    for pid, ptitle, pcontent in db.pages():
        try:
            extractor.extract(pid, pcontent)
        except Exception as e:
            logging.warning('exception %r: page_id(%d)', e, page_id)

    db.close()
else:
    import sys
    extractor.extract(0, open(sys.argv[1]).read())
