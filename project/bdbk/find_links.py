#!/usr/bin/env python

import logging
import re
import unicodedata

from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Q

from bdbk.models import InfoboxTuple, NamedEntity, NamedEntityAlias
from bdbk.textutils.unicode_classifier import is_cjk_char


def split_unicode_by_punctuation(value):
    start = -1
    end = 0

    for end in range(len(value)+1):
        if end < len(value):
            try:
                ctype = unicodedata.name(value[end])
            except ValueError as e:
                ctype = '\n'
        else:
            ctype = '\n'

        if 'CJK' not in ctype and 'LATIN' not in ctype\
           and 'HIRAGANA' not in ctype and 'DIGIT' not in ctype\
           and 'KATAKANA' not in ctype:
            if start != -1:
                yield (value[start:end], start, end)
                start = -1
            else:
                start = end
        else:
            if start == -1:
                start = end

def strip_links(value):
    links = []
    stripped_len = [0]
    def _strip(regx_match):
        value_len = len(regx_match.group(3))
        match_len = regx_match.end() - regx_match.start()
        this_stripped_len = match_len - value_len
        links.append({
            'start': regx_match.start()-stripped_len[0],
            'end': regx_match.end()-stripped_len[0]-this_stripped_len,
            'link_type': regx_match.group(1),
            'link_to': regx_match.group(2)
        })
        stripped_len[0] += this_stripped_len
        return regx_match.group(3)
    return links, re.sub(r'\{\{([a-zA-Z_]+):([^|]+)\|([^}]+)\}\}', _strip, value)

def find_links_in_tuples():
    all_tuples = InfoboxTuple.objects.all()

    paginator = Paginator(all_tuples, 100)
    for i in xrange(1, paginator.num_pages+1):
        tuples = paginator.page(i)

        for tuple in tuples:
            existing_links, content = strip_links(tuple.content)
            new_links = []
            for meaningful, start, end in split_unicode_by_punctuation(content):
                try:
                    search_alias = NamedEntityAlias.objects.get(link_from=meaningful)
                    new_links.append({
                        'start': start,
                        'end': end,
                        'link_type': 'alias_id',
                        'link_to': search_alias.pk
                    })
                except ObjectDoesNotExist as e:
                    pass

                # should not cause circular links
                search_ne = NamedEntity.objects.filter(Q(name__iexact=meaningful)|Q(search_term__iexact=meaningful),\
                                                       ~Q(pk__exact=tuple.named_entity.pk))
                for ne in search_ne:
                    new_links.append({
                        'start': start,
                        'end': end,
                        'link_type': 'ne_id',
                        'link_to': ne.pk
                    })

            if len(new_links) != 0:
                print 'Found new links for tuple (%s,%s,%s)' % (tuple.named_entity.name, tuple.verb.name, tuple.content),\
                    new_links
