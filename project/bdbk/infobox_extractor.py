#!/usr/bin/python

import code
import re
import urllib2
from StringIO import StringIO

from lxml import etree

from .textutils.process_relations import cleanup_verb


def get_inner_text_with_hrefs(element):
    skip_tags = ['script', 'img', 'sup']
    continue_tags = ['a', 'b', 'u', 'i', 'span']
    newpara_tags = ['div', 'br', 'p', 'dt', 'dd']

    def node_text(node, isfirst=False):
        def clean_text(txt):
            return re.sub(r'[\n\t\r ]+', ' ', txt)

        builder = []

        if node.text is not None:
            nodetext = clean_text(node.text)
        else:
            nodetext = None

        if node.tag.lower() == 'a':
            if nodetext is not None:
                # special case for a
                href = node.get('href', None)
                if href: builder.append('{{link:%s|%s}}' % (href, nodetext))
                else: builder.append(nodetext)
        elif node.tag.lower() in skip_tags:
            return ''
        elif node.tag.lower() in continue_tags:
            if nodetext is not None:
                builder.append(nodetext)
        elif node.tag.lower() in newpara_tags:
            if not isfirst:
                builder.append('\n')
            if nodetext is not None:
                builder.append(nodetext)
        else:
            raise KeyError('tag:%s not found' % node.tag.lower())

        for child in node:
            builder.append(node_text(child))
            if child.tail is not None:
                builder.append(clean_text(child.tail))

        return ''.join(builder)

    return node_text(element, True)

def infobox_extractor_1(root):
    def extract_half_infobox(sideid):
        bititle_xpath_template = '//*[@id="baseInfoWrapDom"]/div[%d]/div[%%d]/div/span' % sideid
        bicontent_xpath_template = '//*[@id="baseInfoWrapDom"]/div[%d]/div[%%d]/div/div' % sideid
        bicontent_multiline_xpath_template = '//*[@id="baseInfoWrapDom"]/div[%d]/div[%%d]/div[@class="biOpenItem"]/div[@class="biOpenItemCon"]/div[@class="biOpenContent"]' % sideid

        counter = 1
        while True:
            bititle_elements = root.xpath(bititle_xpath_template % counter)
            bicontent_elements = root.xpath(bicontent_xpath_template % counter)

            if len(bititle_elements) != 1 or len(bicontent_elements) != 1:
                # if both are zero, we are exiting
                if len(bititle_elements) == 0 and len(bicontent_elements) == 0:
                    break
                else:
                    # some bicontent have multi-lines
                    if len(bititle_elements) == 1 and len(bicontent_elements) > 1:
                        bicontent_elements_multiline = root.xpath(bicontent_multiline_xpath_template % counter)
                        if len(bicontent_elements_multiline) != 1:
                            error = 'extractor1: should find len(bicontent_elements_multiline)==1, but'\
                                    'got %d' %  len(bicontent_elements_multiline)
                            raise ValueError(error)

                        bicontent_elements = bicontent_elements_multiline
                    else:
                        # we are having trouble
                        error = 'extractor1: should exit with (len(bititle)==0 and len(bicontent)==0), but '\
                                'got (len(bititle)=%d, len(bicontent)=%d)' % (len(bititle_elements), len(bicontent_elements))
                        raise ValueError(error)

            bititle = get_inner_text_with_hrefs(bititle_elements[0])
            bicontent = get_inner_text_with_hrefs(bicontent_elements[0])
            yield cleanup_verb(bititle), bicontent

            counter += 1

    return list(extract_half_infobox(1)) + list(extract_half_infobox(2))

def infobox_extractor_2(root):
    def extract_half_infobox(sideid):
        bititle_xpath_template = '//*[@class="basic-info"]/dl[%d]/dt[%%d]' % sideid
        bicontent_xpath_template = '//*[@class="basic-info"]/dl[%d]/dd[%%d]' % sideid

        counter = 1
        while True:
            bititle_elements = root.xpath(bititle_xpath_template % counter)
            bicontent_elements = root.xpath(bicontent_xpath_template % counter)

            if len(bititle_elements) != 1 or len(bicontent_elements) != 1:
                # both are zero, we are exiting
                if len(bititle_elements) == 0 and len(bicontent_elements) == 0:
                    break
                else:
                    error = 'extractor2: should exit with (len(bititle)==0 and len(bicontent)==0), but '\
                            'got (len(bititle)=%d, len(bicontent)=%d)' % (len(bititle_elements), len(bicontent_elements))
                    raise ValueError(error)

            bititle = get_inner_text_with_hrefs(bititle_elements[0])
            bicontent = get_inner_text_with_hrefs(bicontent_elements[0])
            yield cleanup_verb(bititle), bicontent

            counter += 1

    return list(extract_half_infobox(1)) + list(extract_half_infobox(2))


def extract_from_etree(etree):
    return list(infobox_extractor_1(etree)) + list(infobox_extractor_2(etree))

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(
        description='extract tuples from page.')
    parser.add_argument('--url', required=True, help='HTML page url.')

    args = parser.parse_args()

    page_source = urllib2.urlopen(args.url).read()

    parser = etree.HTMLParser()
    page = etree.parse(StringIO(page_source), parser)

    tuples = infobox_extractor_1(page) + infobox_extractor_2(page)
    for v,c in tuples:
        print v,c
