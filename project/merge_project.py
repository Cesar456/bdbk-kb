#!/usr/bin/python
# -*- coding: utf8 -*-

import re

import jieba
from django.core.exceptions import ObjectDoesNotExist
from django.db import connection

import project.setup_database
from bdbk.models import InfoboxTuple as BaiduInfoboxTuple
from processor.models import SimilarNamedEntity
from textutils.unicode_classifier import is_good_char
from zhwiki.models import Relation as ZhWikiRelation

jieba.initialize()

def is_identity_content(str1, str2, coef=0.8):
    '''Determine whether two strings are similar,
    using bags of word assumption'''

    lst1 = set(x for x in jieba.cut(str1, cut_all=True) if is_good_char(x) and x.strip())
    lst2 = set(x for x in jieba.cut(str2, cut_all=True) if is_good_char(x) and x.strip())

    # print 'lst1:', ','.join(lst1)
    # print 'lst2:', ','.join(lst2)
    # print 'common:', ','.join(lst1 & lst2)
    if len(lst1) == 0 or len(lst2) == 0:
        # dont compare with empty list
        return False

    common_length = len(lst1 & lst2)
    # TODO: stop words
    avg_length = min(len(lst1),len(lst2))
    if common_length >= coef * avg_length and common_length > 0:
        return True
    else:
        return False

ref_regx = re.compile(r'\[\d+\]')
link_regx = re.compile(r'\{\{link\:.*?\|(.*?)\}\}')

def process_name(bdbk_id, zhwiki_id, threshold=1):
    def preprocess_content(content):
        content = re.sub(ref_regx, '', x.content)
        content = re.sub(link_regx, lambda x: x.group(1), x.content)
        return content

    bdr = BaiduInfoboxTuple.objects.filter(named_entity_id=bdbk_id).all()
    zwr = ZhWikiRelation.objects.filter(named_entity_id=zhwiki_id).all()

    bdr = [preprocess_content(x.content) for x in bdr]
    # print '\n'.join(bdr)
    # print '*' * 20
    zwr = [preprocess_content(x.content) for x in zwr]
    # print '\n'.join(zwr)

    common_tuples = 0
    for i in zwr:
        for j in bdr:
            if is_identity_content(i, j):
                common_tuples += 1

    return common_tuples >= threshold, common_tuples, len(bdr), len(zwr)

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(
        description='Merge named entities from baidu and zhwiki that look the same.')
    parser.add_argument('--log', required=True, help='log file name.')
    parser.add_argument('--icase', type=bool, help='case-insensitive compare between page title.')

    args = parser.parse_args()
    log_fn = args.log
    icase = args.icase

    from project.setup_logging import setup as setup_logger
    logging = setup_logger(log_fn)
    logging.info('Starting merger...')

    def get_pages_with_same_name():
        cursor = connection.cursor()
        # cursor.execute("SELECT count(*) FROM zhwiki_namedentity \
        #     INNER JOIN bdbk_namedentity \
        #     ON zhwiki_namedentity.name=bdbk_namedentity.name")
        # row = cursor.fetchone()
        # row_count = row[0]
        # logging.info('There are %d same entities')

        if icase:
            cursor.execute("SELECT bdbk_namedentity.id, zhwiki_namedentity.id, zhwiki_namedentity.search_term \
                FROM zhwiki_namedentity \
                INNER JOIN bdbk_namedentity \
                ON UPPER(zhwiki_namedentity.search_term)=UPPER(bdbk_namedentity.search_term)")
        else:
            cursor.execute("SELECT bdbk_namedentity.id, zhwiki_namedentity.id, zhwiki_namedentity.search_term \
                FROM zhwiki_namedentity \
                INNER JOIN bdbk_namedentity \
                ON zhwiki_namedentity.search_term=bdbk_namedentity.search_term")

        result = cursor.fetchall()
        return result

    pages = get_pages_with_same_name()
    logging.info('There are %d pages with same name', len(pages))

    for bdbk_id, zhwiki_id, page_name in pages:
        success, common, len_left, len_right =\
            process_name(bdbk_id, zhwiki_id)

        logging.info('%s(bdbk:%d, zhwiki:%d) looks %s (%d of [%d,%d])', 
            page_name, bdbk_id, zhwiki_id,
            'the same' if success else 'different',
            common, len_left, len_right)
