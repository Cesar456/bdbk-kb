#!/usr/bin/python
# -*- coding: utf8 -*-

import re
import sys

from unicode_classifier import *

closure = re.compile(\
    ur'^\[(.*?)\]$|' + ur'^\[+(.*?)$|' + ur'^(.*?)\]+$|' + \
    ur'^【(.*?)】$|' + ur'^【+(.*?)$|' + ur'^(.*?)】+$|' + \
    ur'^“(.*?)”$')

bulletin = re.compile(\
    ur'^\:+(.*?)$|' + ur'^(.*?)\:+$|' + ur'^\:+(.*?)\:+$|' \
    ur'^·+(.*?)$|' + ur'^(.*?)·+$|' + ur'^·+(.*?)·+$|' + \
    ur'^[,\.\|;]+(.*?)$|' + ur'^(.*?)[,\.\|;]+$')

meaning_less_relation = re.compile(\
    ur'^\d+$'
    )

confusing_unicode_spaces = re.compile(\
    u'[\u200B\uE812\u200D\uFEFF\\s?。]')

def get_content_from_regx(regx, s):
    match = re.match(regx, s)
    if match:
        try:
            return next(item for item in match.groups() if item)
        except StopIteration as e:
            # nothing remains...
            return u''

    return s

def cleanup_verb(verb):
    verb = unicode_full_width_to_half(verb).strip()
    verb = re.sub(confusing_unicode_spaces, '', verb)
    verb = get_content_from_regx(closure, verb)
    verb = get_content_from_regx(bulletin, verb)

    return verb

if __name__ == '__main__':
    freqdist = dict()
    if len(sys.argv) < 3:
        print '''This script reduces verbs from a list to normal form, counts them, 
and sorts them in a reversed order.
'''
        sys.exit(1)
    input = sys.argv[1]
    output = sys.argv[2]
    f = open(input)

    for i in f:
        line = i.rstrip().decode('utf8')
        #line, count = line.split('\t')
        line = cleanup_verb(line)
        #count = int(count)

        if not line:
            # nothing remains...
            continue

        if line not in freqdist:
            freqdist[line] = 1#count
        else:
            freqdist[line] += 1#count

    f.close()

    dist = [(x, y) for x, y in freqdist.items()]
    dist = sorted(dist, key=lambda x: x[1], reverse=True)
    dist = [x for x in dist if x[1] >= 3]
    f = open(output, 'w')
    for i in dist:
        f.write(i[0].encode('utf8'))
        f.write('\t')
        f.write(str(i[1]))
        f.write('\n')

    f.close()
