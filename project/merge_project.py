#!/usr/bin/python
# -*- coding: utf8 -*-

from unicode_classifier import is_good_char
import jieba

def is_identity_content(str1, str2, coef=0.7):
    '''Determine whether two strings are similar,
    using bags of word assumption'''

    lst1 = set(x for x in jieba.cut(str1, cut_all=False) if is_good_char(x))
    lst2 = set(x for x in jieba.cut(str2, cut_all=False) if is_good_char(x))

    print 'lst1:', ','.join(lst1)
    print 'lst2:', ','.join(lst2)
    print 'common:', ','.join(lst1 & lst2)
    
    common_length = len(lst1 & lst2)
    minimal_length = min(len(lst1), len(lst2))
    if common_length >= coef * minimal_length:
        return True
    else:
        return False

if __name__ == '__main__':
    s1 = u'浙江省绍兴府会稽县'
    s2 = u'浙江省绍兴府会稽县 (今浙江省绍兴市绍兴县)'
    print is_identity_content(s1, s2)