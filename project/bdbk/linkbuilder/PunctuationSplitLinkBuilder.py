# -*- coding: utf-8 -*-
import unicodedata

from .LinkBuilder import LinkBuilder


def split_unicode_by_punctuation(value):
    '''
    split a unicode string by all non-character chars.
    e.g.
    "需要——截断【的句子"
    ==>
    ["需要", "截断", "的句子"]
    '''
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

class PunctuationSplitLinkBuilder(LinkBuilder):
    '''
    将三元组值按非CJK字符分开查找
    '''
    def find_links(self, *args, **kwargs):
        for tuple in self.infobox_iterator():
            existing_links, content = self.strip_links(tuple.content)
            new_links = []
            for meaningful, start, end in split_unicode_by_punctuation(content):
                for obj, is_ne_or_alias in self.resolve_name(meaningful):
                    new_links.append({
                        'start': start,
                        'end': end,
                        'link_type': 'ne_id' if is_ne_or_alias else 'alias_id',
                        'link_to': obj.pk
                    })

            if len(new_links) != 0:
                print 'Found new links for tuple (%s,%s,%s)' % (tuple.named_entity.name, tuple.verb.name, tuple.content),\
                    new_links
