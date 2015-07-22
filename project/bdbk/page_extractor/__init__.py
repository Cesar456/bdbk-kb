# -*- coding:utf-8 -*-

import re
from StringIO import StringIO

from lxml import etree

from .infobox_extractor import extract_from_etree
from bdbk.textutils.process_relations import cleanup_verb


class Extractor(object):
    lemma_list_link = re.compile(r'<a.*?href=["\']*([^"\']+)["\']*.*?>(.*?)</a>')

    def __init__(self):
        pass

    def get_tuples(self, html):
        '''Handles a real page, returns its tuple list
        '''
        return extract_from_etree(html)

    def get_title(self, html):
        # page title
        page_title = html.xpath("//head//title//text()")
        if len(page_title) == 1 and u'_百度百科' in page_title[0]:
            page_title = page_title[0]
            page_title = page_title[:page_title.rfind('_')]

            return page_title
        else:
            return None

    def get_search_term(self, html):
        # search term
        search_term = html.xpath("//input[@id='topword']//@value")
        if len(search_term) == 1:
            return unicode(search_term[0])
        else:
            return None

    def get_abstract(self, html):
        # abstract
        page_abstract = html.xpath("//head//meta[@name='Description']//@content")
        if len(page_abstract) == 1:
            return unicode(page_abstract[0])
        else:
            return None

    def get_lemma_list(self, html):
        lemmas = html.xpath("//div[@id='lemma-list']//ul//a")
        result = []
        for i in lemmas:
            result.append(u'{{link:%s|%s}}' % (i.xpath('./@href')[0], i.xpath('./text()')[0]))
        return result

    def is_lemma_list(self, html):
        return len(html.xpath("//*[@id='lemma-list']")) != 0

    def get_cat_list(self, html):
        for i in html.xpath('//*[@class="taglist"]'):
            yield ''.join([x.strip() for x in i.itertext()])

    def extract(self, content):
        '''
        Returns:
        (page_title, search_term, infoboxtuples)

        infoboxtuples -> [tuple, ...]
        tuple -> (verb, content)
        '''
        parser = etree.HTMLParser(encoding='utf8')
        page = etree.parse(StringIO(content), parser)

        title = self.get_title(page)
        search_term = self.get_search_term(page)
        if not search_term: search_term = title

        # if not self.is_lemma_list(page):
        # abstract = self.get_abstract(page)
        tuples = self.get_tuples(page)
        cat_list = self.get_cat_list(page)

        return (title, search_term, cat_list, tuples)


extractor = Extractor()
