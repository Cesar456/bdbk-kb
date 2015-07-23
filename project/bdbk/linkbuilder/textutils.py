# -*- coding: utf-8 -*-
import re
import unicodedata


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

def strip_links(value):
    '''
    strip all links in a string, return the links list and the stripped string.
    e.g.:
    "This is a {{link:/url.htm|test}}"
    ==>
    [{'start':10, 'end': 14, 'link_type': 'link', 'link_to': 'url.htm'}], "This is a test"
    '''
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
