# -*- coding: utf-8 -*-
from .LinkBuilder import LinkBuilder


class EntireValueLinkBuilder(LinkBuilder):
    '''
    将整个属性值放入数据库中查找。
    '''
    def find_links(self, *args, **kwargs):
        for tuple in self.infobox_iterator():
            new_links = []
            existing_links, content = self.strip_links(tuple.content)

            for obj, is_ne_or_alias in self.resolve_name(content):
                new_links.append({
                    'start': 0,
                    'end': len(content),
                    'link_type': 'ne_id' if is_ne_or_alias else 'alias_id',
                    'link_to': obj.pk
                })

            if len(new_links) != 0:
                print 'Found new links for tuple (%s,%s,%s)' % (tuple.named_entity.name, tuple.verb.name, tuple.content),\
                    new_links, existing_links
