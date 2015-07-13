# -*- coding:utf-8 -*-

import re
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

    def extract(self, content):
        '''
        Returns:
        (page_title, search_term, infoboxtuples)

        infoboxtuples -> [tuple, ...]
        tuple -> (verb, content)
        '''
        parser = etree.HTMLParser()
        page = etree.parse(StringIO(content), parser)

        title = self.get_title(page)
        search_term = self.get_search_term(page)
        if not search_term: search_term = title

        # if not self.is_lemma_list(page):
        # abstract = self.get_abstract(page)
        tuples = self.get_tuples(page)

        return (title, search_term, tuples)


extractor = Extractor()
