# -*- coding: utf-8 -*-
import re
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
           and 'KATAKANA' not in ctype\
           and (end<len(value) and value[end] != u'·'): # foreign names

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
                        'link_to': obj
                    })

            self.find_links_with_same_category(tuple, new_links)

    def find_links_with_same_category(self, tuple, new_links):
        # find common cat
        if len(new_links) < 2:
            return

        cats = None
        ne_looked_up = []
        def drop_redundant_ne(ne):
            '''
            Drop nes that are very same.
            '''
            url = ne.bdbk_url
            match = re.search(r'http://baike.baidu.com/view/(\d+).htm|http://baike.baidu.com/subview/(\d+)/(\d+.htm)', url)
            if not match:
                return True

            view_id, subview_major_id, subview_minor_id = match.groups()
            if view_id is not None:
                if (view_id, view_id) not in ne_looked_up:
                    ne_looked_up.append((view_id, view_id))
                    return False
            if subview_major_id is not None and subview_minor_id is not None:
                t = (subview_major_id, subview_minor_id)
                if t not in ne_looked_up:
                    ne_looked_up.append(t)
                    return False

            return True

        for link in new_links:
            if link['link_type'] == 'ne_id':
                ne = link['link_to']
            else:
                ne = link['link_to'].link_to

            if drop_redundant_ne(ne):
                continue

            this_cats = set([x.name for x in ne.categories.all()])
            if cats is None:
                cats = this_cats
            else:
                cats = cats & this_cats

            if not cats:
                break

        if cats:
            print '=' * 20
            print 'Found new links for tuple (%s,%s,%s)' % (tuple.named_entity.name, tuple.verb.name, tuple.content)
            print 'common categories: ', ','.join(cats)
            print 'new_links:'
            for link in new_links:
                print 'link type:', link['link_type'],
                if link['link_type'] == 'ne_id':
                    print ', link to:', link['link_to'].name
                else:
                    print ', link to:', link['link_to'].link_to.name
            print '=' * 20
