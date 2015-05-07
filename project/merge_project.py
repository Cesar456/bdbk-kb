#!/usr/bin/python
# -*- coding: utf8 -*-

from unicode_classifier import is_good_char
from setup_database import *
from django.core.exceptions import ObjectDoesNotExist
import jieba
import re
jieba.initialize()

def is_identity_content(str1, str2, coef=0.8):
    '''Determine whether two strings are similar,
    using bags of word assumption'''

    lst1 = set(x for x in jieba.cut(str1, cut_all=True) if is_good_char(x))
    lst2 = set(x for x in jieba.cut(str2, cut_all=True) if is_good_char(x))

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

def process_name(bdne, zhwikine):
    def remove_duplicate(lst):
        e = []
        r = []
        for i in lst:
            s = '%d%s' % (i.named_entity_id, i.content)
            if s not in e:
                e.append(s)
                r.append(i)
            else:
                i.delete()

        return r

    def preprocess_content(content):
        content = re.sub(ref_regx, '', x.content)
        content = re.sub(link_regx, lambda x: x.group(1), x.content)
        return content

    bdr = BaiduRelation.objects.filter(named_entity_id=bdne).all()
    zwr = ZhWikiRelation.objects.filter(named_entity_id=zhwikine).all()

    bdr = remove_duplicate(bdr)
    zwr = remove_duplicate(zwr)

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
                print '-' * 20
                print i
                print j

    print 'Result: %d/(%d,%d)' % (common_tuples, len(bdr), len(zwr))

if __name__ == '__main__':
    for i in BaiduNamedEntity.objects.iterator():
        raw_input()
        try:
            j = ZhWikiNamedEntity.objects.get(name=i.name)
            process_name(i.pk, j.pk)
        except ObjectDoesNotExist as e:
            pass