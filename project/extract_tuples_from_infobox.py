#!/usr/bin/python
# -*- coding: utf-8 -*-
# This script reads baidu baike data, and parses its infobox, produces
# tuples of the name entities

import gzip
import logging
import os
import re
import sys
from StringIO import StringIO

from lxml import etree

from textutils.process_relations import cleanup_verb


class Extractor(object):
    lemma_list_link = re.compile(r'<a.*?href=["\']*([^"\']+)["\']*.*?>(.*?)</a>')

    def __init__(self):
        pass

    def get_tuples(self, html):
        '''Handles a real page, returns its tuple list
        '''
        tuples = []

        page_biitems = html.xpath("//*[@class='biItem']")
        for i in page_biitems:
            page_bititle = i.xpath(".//*[@class='biTitle']//text()")
            if len(page_bititle) == 0:
                continue

            bititle = re.sub(r'[\xa0\s]', '', ''.join(page_bititle))
            bititle = cleanup_verb(bititle)
            if not bititle:
                continue

            # if we have a <br>, then multiple bicontents should be produced
            page_bicontents = i.xpath(".//*[@class='biContent']//text()|.//a")
            target = ''

            in_href=False
            for bicontent in page_bicontents:
                if not isinstance(bicontent, unicode) and not isinstance(bicontent, str):
                    if in_href:
                        target += '}}'

                    in_href = True
                    href = bicontent.xpath('./@href')
                    if len(href):
                        # some links are just clickable HTML of foot-reference,
                        # so we don't have to include them
                        target += '{{link:%s|' % href[0]
                    else:
                        in_href = False
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
        page_title = html.xpath("//head//title//text()")
        if len(page_title) == 1 and u'_百度百科' in page_title[0]:
            page_title = page_title[0]
            page_title = page_title[:page_title.rfind('_')]

            return page_title
        else:
            # logging.warning('Unable to extract title: page_id(%d)', page_id)
            return None

    def get_search_term(self, html):
        # search term
        search_term = html.xpath("//input[@id='topword']//@value")
        if len(search_term) == 1:
            return search_term[0]
        else:
            return None

    def get_abstract(self, html):
        # abstract
        page_abstract = html.xpath("//head//meta[@name='Description']//@content")
        if len(page_abstract) == 1:
            return page_abstract[0]
        else:
            return None

    def get_lemma_list(self, html):
        lemmas = html.xpath("//div[@id='lemma-list']//ul//a")
        result = []
        for i in lemmas:
            result.append('{{link:%s|%s}}' % (i.xpath('./@href')[0], i.xpath('./text()')[0]))
        return result

    def is_lemma_list(self, html):
        return len(html.xpath("//*[@id='lemma-list']")) != 0

    def extract(self, page_id, content):
        parser = etree.HTMLParser()
        page = etree.parse(StringIO(content), parser)

        title = self.get_title(page)
        search_term = self.get_search_term(page)
        if not search_term: search_term = title

        if not self.is_lemma_list(page):
            abstract = self.get_abstract(page)
            tuples = self.get_tuples(page)

            return (title, search_term, abstract, tuples)
        else:
            lemmas = self.get_lemma_list(page)

            return (title, lemmas)

extractor = Extractor()

if __name__ == '__main__':
    import argparse
    from dbutils.baidu_database import BaiduDatabase
    import project.setup_database
    from bdbk.models import *
    import time

    parser = argparse.ArgumentParser(
        description='I will read baidu baike and produce you the info tuples of its infobox.')
    parser.add_argument('--src', required=True, choices=['stdin', 'page', 'archive'], help='extract from page source.')
    parser.add_argument('--page-source', type=str, help='page source(page mode).')
    parser.add_argument('--archive-dir', type=str, help='archive dir(archive mode).')
    parser.add_argument('--archive-name', type=str, help='name of the archive(archive mode).')
    parser.add_argument('--log', help='log file name.')

    args = parser.parse_args()
    src = args.src

    def do_data_archive(archive_dir, archive_name):
        db = BaiduDatabase(archive_dir, archive_name)
        verb_dict = {}

        processed_count = 0
        last_time = time.time()
        last_processed = 0

        for pid, ptitle, pcontent in db.all_pages():
            processed_count += 1
            if processed_count % 1000 == 0:
                logging.info('%d processed in %d/sec', processed_count, (processed_count-last_processed)/(time.time()-last_time))
                last_processed = processed_count
                last_time = time.time()

            try:
                info = extractor.extract(pid, pcontent)
                if len(info) == 4:
                    title, search_term, abstract, tuples = info
                    if len(tuples) > 0:
                        ne = NamedEntity(name=title,
                                         search_term=search_term,
                                         abstract=abstract,
                                         page_id=pid)
                        ne.save()

                        npk = ne.pk
                        for tuple in tuples:

                            if tuple[0] not in verb_dict:
                                v, _ = Verb.objects.get_or_create(name=tuple[0])
                                verb_dict[tuple[0]] = v.pk
                                vpk = v.pk
                            else:
                                vpk = verb_dict[tuple[0]]

                            t = InfoboxTuple(named_entity_id=npk,
                                             content=tuple[1],
                                             verb_id=vpk)
                            t.save()

                elif len(info) == 2:
                    title, lemmas = info
                    for lemma in lemmas:
                        ner = NamedEntityRedirect(page_id=pid,
                                                  name=title,
                                                  linked_name=lemma)
                        ner.save()

            except Exception as e:
                logging.warning('exception %r: page_id(%d)', e, pid)

        db.close()

    if src == 'page':
        if not args.page_source:
            logging.error('page mode specified, but no page source found in console arguments.')
            sys.exit(1)

    if src == 'archive':
        archive_dir = args.archive_dir
        archive_name = args.archive_name
        if not archive_dir or not archive_name:
            logging.error('archive mode specified, but no archive found in console arguments.')
            sys.exit(1)

    if args.log:
        from project.setup_logging import setup as setup_logger
        logging = setup_logger(log_fn)
        logging.info('Source: %s in %s', db_name, dir)

    if src == 'stdin' or src == 'page':
        if src == 'stdin':
            inputs = []
            while True:
                try:
                    inputs.append(raw_input())
                except EOFError as e:
                    break

            source = '\n'.join(inputs)
        else:
            source = open(args.page_source).read()

        info = extractor.extract(0, source)
        if len(info)==4:
            print 'Info tuples:'
            title, search_term, abstract, tuples = info
            print 'Title:', title
            print 'Search Term:', search_term
            print 'Abstract:', abstract

            for tuple in tuples:
                print '(', tuple[0], ',', tuple[1], ')'
        elif len(info) == 2:
            print 'Page Redirect:'
            title, lemmas = info
            print 'Title:', title
            for lemma in lemmas:
                print '==>', lemma

    elif src == 'archive':
        do_data_archive(archive_dir, archive_name)
