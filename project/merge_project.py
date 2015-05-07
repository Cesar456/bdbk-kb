#!/usr/bin/python
# -*- coding: utf8 -*-

from unicode_classifier import is_good_char
import jieba

def is_identity_content(str1, str2, coef=0.9):
    '''Determine whether two strings are similar,
    using bags of word assumption'''

    lst1 = set(x for x in jieba.cut(str1, cut_all=False) if is_good_char(x))
    lst2 = set(x for x in jieba.cut(str2, cut_all=False) if is_good_char(x))

    #print 'lst1:', ','.join(lst1)
    #print 'lst2:', ','.join(lst2)
    #print 'common:', ','.join(lst1 & lst2)

    common_length = len(lst1 & lst2)
    avg_length = (len(lst1) + len(lst2)) / 2
    if common_length >= coef * avg_length and common_length > 0:
        return True
    else:
        return False

if __name__ == '__main__':
    clst1 = open('zhwiki_relation.csv').read().decode('utf8').splitlines()
    clst2 = open('bdbk_relation.csv').read().decode('utf8').splitlines()

    print 'Guessed identical sentences:'
    for i in clst1:
        for j in clst2:
            if is_identity_content(i,j):
                print '-' * 20
                print i
                print j
                #print is_identity_content(i, j)