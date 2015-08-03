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

            links_by_pos = {}
            for meaningful, start, end in split_unicode_by_punctuation(content):
                if meaningful == tuple.named_entity.search_term or\
                   meaningful == tuple.named_entity.name:
                    # never link to self
                    continue

                key = (start,end)
                value = None
                for obj, is_ne_or_alias in self.resolve_name(meaningful):
                    if not value:
                        value = []
                        links_by_pos[key] = value

                    d = {}
                    if is_ne_or_alias:
                        d['link_type'] = 'ne_id'
                        d['link_to'] = obj
                        d['cats'] = [x.name for x in obj.categories.all()]
                    else:
                        d['link_type'] = 'alias_id'
                        d['link_to'] = obj
                        d['cats'] = [x.name for x in obj.link_to.categories.all()]
                    value.append(d)

            new_links = self.find_links_with_same_category(links_by_pos)
            if new_links:
                print '=' * 40
                print tuple.named_entity.name, tuple.verb.name, tuple.content
                for k, v in new_links.items():
                    if v['link_type'] == 'ne_id':
                        print k, v['link_to'].name,
                    else:
                        print k, v['link_to'].link_from,
                print ''

    def find_links_with_same_category(self, links_by_pos):
        # too few, can't be sure
        if len(links_by_pos) < 2:
            return

        matched_idx = []
        idx = [-1] * len(links_by_pos)
        cmn_cats = [None]

        def _iterator(depth, keys):
            pos_link = links_by_pos[keys[depth]]

            for i in range(len(pos_link)):
                idx[depth] = i

                if depth==0:
                    cmn_cats[0] = set(pos_link[i]['cats'])
                    _iterator(depth+1, keys)
                else:
                    cmn_cats_old = cmn_cats[0]
                    cmn_cats_ = cmn_cats_old & set(pos_link[i]['cats'])
                    if not cmn_cats_:
                        continue

                    if depth==len(keys)-1:
                        if len(cmn_cats_):
                            matched_idx.append(
                                (len(cmn_cats_), list(idx))
                            )
                    else:
                        cmn_cats[0] = cmn_cats_
                        _iterator(depth+1, keys)
                        cmn_cats[0] = cmn_cats_old

        keys = links_by_pos.keys()
        _iterator(0, keys)

        if not matched_idx:
            return None

        matched_idx = sorted(matched_idx, key=lambda x: x[0], reverse=True)
        idx = matched_idx[0][1]
        result = {}
        for i in range(len(idx)):
            key = keys[i]
            lst = links_by_pos[keys[i]]
            link = lst[idx[i]]
            result[key] = {
                'link_type': link['link_type'],
                'link_to': link['link_to'],
            }

        return result
