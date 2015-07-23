# -*- coding: utf-8 -*-
import logging
import os
import re
import subprocess

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q

from bdbk.models import InfoboxTuple, NamedEntity, NamedEntityAlias
from .textutils import split_unicode_by_punctuation, strip_links

from .iterator import iterator

def find_name_in_db(tuple, s, start, end, new_links):
    '''
    find a name in db.
    s:
    start: start index of name.
    end: end index of name.
    new_links: a list of a links found.
    '''
    name = s[start:end]
    try:
        search_alias = NamedEntityAlias.objects.get(link_from=name)
        new_links.append({
            'start': start,
            'end': end,
            'link_type': 'alias_id',
            'link_to': search_alias.pk
        })
    except ObjectDoesNotExist as e:
        pass

    # no self reference
    search_ne = NamedEntity.objects.filter(Q(name__iexact=name)|Q(search_term__iexact=name),\
                                           ~Q(pk__exact=tuple.named_entity.pk))
    for ne in search_ne:
        new_links.append({
            'start': start,
            'end': end,
            'link_type': 'ne_id',
            'link_to': ne.pk
        })

def find_maximum_names():
    pipe = subprocess.Popen(os.path.dirname(__file__) + '/max_common_string_in_set',
                            stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            bufsize=0)

    # FIXME: newline char replace?
    for i in iterator(NamedEntityAlias):
        pipe.stdin.write(i.link_from.upper().encode('utf8'))
        pipe.stdin.write('\t')
        pipe.stdin.write('alias_id:%d\n' % i.pk)
    for i in iterator(NamedEntity):
        pipe.stdin.write(i.name.upper().encode('utf8'))
        pipe.stdin.write('\t')
        pipe.stdin.write('ne_name\n')
        pipe.stdin.write(i.search_term.upper().encode('utf8'))
        pipe.stdin.write('\t')
        pipe.stdin.write('ne_st\n')

    pipe.stdin.write('\n')
    pipe.stdin.flush()

    for tuple in iterator(InfoboxTuple):
        new_links = []
        existing_links, content = strip_links(tuple.content)

        # newline char will mess up everything
        pipe.stdin.write(content.replace('\n', '.').upper().encode('utf8'))
        pipe.stdin.write('\n')
        pos = 0
        while True:
            line = pipe.stdout.readline()
            line = line.strip('\n').decode('utf8')
            if not line:
                break

            if '\t' in line:
                end_pos = pos + len(line.split('\t')[0])
                find_name_in_db(tuple, content, pos, end_pos, new_links)
            else:
                end_pos = pos + len(line)

            pos = end_pos

        if len(new_links):
            print 'Found new links for tuple (%s,%s,%s)' % (tuple.named_entity.name, tuple.verb.name, tuple.content),\
                new_links, existing_links

def find_link_of_entire_value():
    '''
    将整个属性值放入数据库中查找。
    '''
    for tuple in iterator(InfoboxTuple):
        new_links = []
        existing_links, content = strip_links(tuple.content)

        find_name_in_db(tuple, content, 0, len(content), new_links)

        if len(new_links) != 0:
            print 'Found new links for tuple (%s,%s,%s)' % (tuple.named_entity.name, tuple.verb.name, tuple.content),\
                new_links, existing_links

def find_links_split_by_punct():
    '''
    将三元组值按非CJK字符分开查找
    '''
    for tuple in iterator(InfoboxTuple):
        existing_links, content = strip_links(tuple.content)
        new_links = []
        for meaningful, start, end in split_unicode_by_punctuation(content):
            find_name_in_db(tuple, meaningful, start, end, new_links)

        if len(new_links) != 0:
            print 'Found new links for tuple (%s,%s,%s)' % (tuple.named_entity.name, tuple.verb.name, tuple.content),\
                new_links
