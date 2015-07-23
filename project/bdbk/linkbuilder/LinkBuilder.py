import re

from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Q

from bdbk.models import InfoboxTuple, NamedEntity, NamedEntityAlias


class LinkBuilder(object):
    '''
    LinkBuilder: base class of all link builders.

    __init__(self):

    resolve_name(self, name):
        resolve a name to named entities.
        returns: (obj, TF_obj_is_ne_else_alias)

    iterator(self, cls, *args, **kwargs):
        a handy iterator for all objects in database.
        extra parameters will be treated as query dicts.

    infobox_iterator(self, *args, **kwargs):
        a handy iterator for all InfoboxTuple-s.

    find_links(self, *args, **kwargs):
        start this builder.
        must be override by subclasses.

    strip_links(self, content):
        strip all links in string.
    '''
    def resolve_name(self, name):
        try:
            search_alias = NamedEntityAlias.objects.get(link_from=name)
            yield search_alias.link_to, False
        except ObjectDoesNotExist as e:
            pass

        search_ne = NamedEntity.objects.filter(Q(name__iexact=name)|Q(search_term__iexact=name))
        for ne in search_ne:
            yield ne, True

    def iterator(self, cls, *args, **kwargs):
        all = cls.objects.filter(*args, **kwargs).all()
        paginator = Paginator(all, 100)
        for i in xrange(1, paginator.num_pages+1):
            objs = paginator.page(i)
            for obj in objs:
                yield obj

    def infobox_iterator(self, *args, **kwargs):
        for i in self.iterator(InfoboxTuple, *args, **kwargs):
            yield i

    def strip_links(self, content):
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

        return links, re.sub(r'\{\{([a-zA-Z_]+):([^|]+)\|([^}]+)\}\}', _strip, content)

    def find_links(self, *args, **kwargs):
        raise NotImplementedError('must not use base class LinkBuilder as a builder.')
