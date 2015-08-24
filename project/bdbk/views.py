import jieba
import json
import os
import random
import re
import zlib

import pymongo
from bson import objectid
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.db import connection
from django.db.models import Q
from django.http import (Http404, HttpResponse, HttpResponseRedirect,
                         HttpResponseBadRequest)
from django.shortcuts import get_object_or_404, render
from django.utils.html import escape
from django.views.decorators.http import require_http_methods

from .models import (DBVersion, InfoboxTuple, InfoboxTupleLink, NamedEntity,
                     NamedEntityAlias, Verb)


def random_objects(cls, count):
    total_ne_count_approx = approx_count_objects(cls)
    if total_ne_count_approx < 500:
        total_ne_count = cls.objects.all().count()

        random_count = min(count, total_ne_count)
        for i in range(0, random_count):
            random_index = random.randint(0, total_ne_count-1)
            randomed = cls.objects.all()[random_index]

            yield randomed
    else:
        for i in cls.objects.raw('''
            SELECT *
                FROM %s AS r1 JOIN
                    (SELECT CEIL(RAND() *
                        (SELECT MAX(id)
                            FROM %s)) AS id)
            AS r2
            WHERE r1.id >= r2.id
            ORDER BY r1.id ASC
            LIMIT %d''' % (cls._meta.db_table, cls._meta.db_table, count)):
            yield i

def approx_count_objects(cls):
    cursor = connection.cursor()
    cursor.execute("SHOW TABLE STATUS WHERE NAME='%s'" % cls._meta.db_table)
    return cursor.fetchone()[4]

def strip_content_links(content):
    return re.sub(r'\{\{([a-zA-Z_]+):([^|]+)\|([^}]+)\}\}', lambda x:x.group(3), content)

def resolve_content_links(content, infoboxlinks=[]):
    # TODO: add cache
    content = escape(content)


    def strip_obvious_links(content):
        '''
        strip all links in a string, return the links list and the stripped string.
        e.g.:
        "This is a {{link:/url.htm|test}}"
        ==>
        [{'start':10, 'end': 14, 'link_type': 'link', 'link_to': 'url.htm'}], "This is a test"
        '''
        links = {}
        stripped_len = [0]
        def _strip(regx_match):
            value_len = len(regx_match.group(3))
            match_len = regx_match.end() - regx_match.start()
            this_stripped_len = match_len - value_len
            url_real = 'http://baike.baidu.com' + regx_match.group(2)
            linked_ne = NamedEntity.objects.filter(bdbk_url=url_real)
            if linked_ne:
                start = regx_match.start()-stripped_len[0]
                end = regx_match.end()-stripped_len[0]-this_stripped_len
                links[(start,end)] = reverse('ShowTuplesForNamedEntity', args=(linked_ne[0].pk,))

            stripped_len[0] += this_stripped_len
            return regx_match.group(3)

        return links, re.sub(r'\{\{([a-zA-Z_]+):([^|]+)\|([^}]+)\}\}', _strip, content)

    links, content = strip_obvious_links(content)

    for i in infoboxlinks:
        mch = re.match(r'\{\{([a-zA-Z_]+):([^|]+)\}\}', i.linkcontent)
        if not mch: continue

        if mch.group(1) == 'alias_id':
            try:
                target = NamedEntityAlias.objects.get(pk=mch.group(2)).link_to
            except ObjectDoesNotExist as e:
                target = None
        elif mch.group(1) == 'ne_id':
            try:
                target = NamedEntity.objects.get(pk=mch.group(2))
            except ObjectDoesNotExist as e:
                target = None
        else:
            target = None

        if target and (i.start, i.end) not in links:
            links[(i.start, i.end)] = reverse('ShowTuplesForNamedEntity', args=(target.pk,))

    links_keys = sorted(links.keys())
    splits = [] # string builder
    start = 0 # current start pos of content[0]
    for s,e in links_keys:
        if s<start: continue

        if s!=start:
            splits.append(content[:s-start])
            content = content[s-start:]
            start += s-start

        part = content[:e-s]
        content = content[e-s:]
        start += e-s
        splits.append('<a href="%s">%s</a>' % (links[(s,e)], part))
    splits.append(content)

    return ''.join(splits)

def populate_db_status():
    # current data status
    total_tuple_count = '~%d' % approx_count_objects(InfoboxTuple)
        # InfoboxTuple.objects.all().count()
    total_verb_count = '~%d' % approx_count_objects(Verb)
        # Verb.objects.all().count()
    total_ne_count = '~%d' % approx_count_objects(NamedEntity)
        # NamedEntity.objects.all().count()

    return {
        'status':{
            'ne_count': total_ne_count,
            'infoboxtuple_count': total_tuple_count,
            'verb_count': total_verb_count,
            'db_version': DBVersion
        }
    }

def populate_random_suggestion():
    # fetch random named entities
    random_nes = []

    for randomed in random_objects(NamedEntity, 6):
        random_nes.append({
            'ne_title': randomed.name,
            'ne_url': reverse('ShowTuplesForNamedEntity', args=(randomed.pk,))
        })

    return {
        'randomnes': random_nes
    }

stopwords = None

def is_in_stopwords(word):
    global stopwords
    if stopwords is None:
        _stopwords = {}
        with open(os.path.dirname(__file__)+'/stopwords.txt') as f:
            for line in f:
                _stopwords[line.rstrip('\n').decode('utf8')] = 1
        stopwords = _stopwords

    return word in stopwords

# views starts

def About(request):
    return render(request, 'bdbk/About.html', {})

def Status_Overview(request):
    return render(request, 'bdbk/Status_Overview.html', populate_db_status())

def Status_Verb(request):
    return HttpResponse('TODO')

def Status_NamedEntity(request, filter_string=None):
    return HttpResponse('TODO')

def AdvancedSearch(request):
    def AdvancedSearch_get(request):
        context = {}
        context.update(populate_random_suggestion())
        context.update(populate_db_status())
        return render(request, 'bdbk/AdvancedSearch_form.html', context)

    def AdvancedSearch_post(request):
        ne_action = request.POST.get('limitNE_action')
        ne_str = request.POST.get('limitNE_str')

        verb_action = request.POST.get('limitVERB_action')
        verb_str = request.POST.get('limitVERB_str')

        content_action = request.POST.get('limitCONTENT_action')
        content_str = request.POST.get('limitCONTENT_str')

        def action_to_query_dict(field, field_friendly_name, action, qstr):
            if action == 'IS':
                a = 'iexact'
                b = '%s is "%s"' % (field_friendly_name, qstr)
            elif action == 'STARTSWITH':
                a = 'istartswith'
                b = '%s starts with "%s"' % (field_friendly_name, qstr)
            elif action == 'ENDSWITH':
                a = 'iendswith'
                b = '%s ends with "%s"' % (field_friendly_name, qstr)
            elif action == 'CONTAINS':
                a = 'icontains'
                b = '%s contains "%s"' % (field_friendly_name, qstr)
            else:
                a = 'icontains'
                b = '%s contains "%s"' % (field_friendly_name, qstr)

            return b, {
                field + '__' + a: qstr
            }

        qdict = []
        friendly_name = []
        if ne_str:
            friendly_name_1, qdict_1 = action_to_query_dict('named_entity__name', 'Name of entity', ne_action, ne_str)
            q = Q(**qdict_1)
            friendly_name.append(friendly_name_1)

            friendly_name_1, qdict_1 = action_to_query_dict('named_entity__search_term', 'Search term of entity', ne_action, ne_str)
            q |= Q(**qdict_1)
            friendly_name.append(friendly_name_1)

            friendly_name_alias, qdict_alias = action_to_query_dict('link_from', 'Name alias', ne_action, ne_str)
            friendly_name.append(friendly_name_alias)
            alias_result = NamedEntityAlias.objects.filter(**qdict_alias).all()
            if alias_result:
                q |= Q(named_entity__pk__in=[x.link_to.pk for x in alias_result])

            qdict.append(q)
        if verb_str:
            friendly_name_2, qdict_2 = action_to_query_dict('verb__name', 'verb', verb_action, verb_str)
            qdict.append(Q(**qdict_2))
            friendly_name.append(friendly_name_2)
        if content_str:
            friendly_name_3, qdict_3 = action_to_query_dict('content', 'attribute value', content_action, content_str)
            qdict.append(Q(**qdict_3))
            friendly_name.append(friendly_name_3)

        if not qdict:
            context = {
                'search_result_message': 'No filter applied.'
            }
        else:
            # TODO: paginator
            qresult = InfoboxTuple.objects.filter(*qdict).order_by('named_entity', 'verb')

            result = []
            for i in qresult:
                result.append({
                    'namedentity': i.named_entity.name,
                    'namedentity_url': reverse('ShowTuplesForNamedEntity', args=(i.named_entity.id,)),
                    'verb': i.verb.name,
                    'content': resolve_content_links(i.content, list(i.infoboxtuplelink_set.all()))
                })

            context = {
                'search_result': result,
                'friendly_query_string': ', '.join(friendly_name),
                'search_result_message': '%d results.' % len(result)
            }

        context.update(populate_db_status())
        return render(request, 'bdbk/AdvancedSearch_result.html', context)

    if request.method == 'POST':
        return AdvancedSearch_post(request)
    else:
        return AdvancedSearch_get(request)

@require_http_methods(['POST'])
def FuzzySearch(request):
    '''
    Fuzzy query strategy:
    1. Named Entity name:
        name,
        search_term
    2. Content:
    3. Verb
    '''

    search_term = request.POST.get('query', None)
    if not search_term:
        return HttpResponseRedirect(reverse('ShowTuplesForNamedEntity', args=('random',)))

    # ne_search_result = NamedEntity.objects.filter(name__startswith=search_term)
    ne_search_result = NamedEntity.objects.filter(name__icontains=search_term)

    search_result_ne = []
    for obj in ne_search_result:
        search_result_ne.append({
            'ne_name': obj.name,
            'ne_url': reverse('ShowTuplesForNamedEntity', args=(obj.pk,))
        })

    tuple_search_result = InfoboxTuple.objects.filter(content__icontains=search_term)

    search_result_content = []
    for obj in tuple_search_result:
        search_result_content.append({
            'ne_name': obj.named_entity.name,
            'ne_url': reverse('ShowTuplesForNamedEntity', args=(obj.named_entity.pk,)),
            'verb': obj.verb.name,
            'content': resolve_content_links(obj.content, list(obj.infoboxtuplelink_set.all())),
        })

    result = {
        'search_term': search_term,
        'search_result_ne': search_result_ne,
        'search_result_content': search_result_content,
    }
    return render(request, 'bdbk/SearchResult.html', result)

def ShowTuplesForNamedEntity(request, nepk):
    if nepk == 'random':
        random_ne = list(random_objects(NamedEntity, 1))[0]
        nepk = random_ne.pk
        return HttpResponseRedirect(reverse('ShowTuplesForNamedEntity', args=(nepk,)))

    nepk = int(nepk)

    ne_object = get_object_or_404(NamedEntity, pk=nepk)

    tuples = []

    for infoboxtuple in ne_object.infoboxtuple_set.all():
        tuples.append({
            'verb': infoboxtuple.verb.name,
            'content': resolve_content_links(infoboxtuple.content, list(infoboxtuple.infoboxtuplelink_set.all())),
        })

    def getCatString(ne_object):
        cat_names = []
        for i in ne_object.categories.all():
            cat_names.append(i.name)

        return ','.join(cat_names)

    result = {
        'nepk': nepk,
        'namedentity':{
            'ne_id': nepk,
            'ne_title': ne_object.name,
            'ne_search_term': ne_object.search_term,
            'ne_last_modified': ne_object.last_modified.strftime('%Y-%m-%d %H:%M:%S') if ne_object.last_modified else 'Not Specified',
            'ne_bdbk_url': ne_object.bdbk_url,
            'ne_infobox': tuples,
            'ne_cats': getCatString(ne_object),
            },
    }
    result.update(populate_random_suggestion())
    result.update(populate_db_status())

    return render(request, 'bdbk/ShowTuplesForNamedEntity.html', result)

def namedEntityLinks(request, nepk):
    '''
    return value:
    {
      "name": "name of ne",

      "tuples": [{
        "id": 0,
        "verb": "some verb",
        "value": "some value",
      }, ...],

      "links": [{
        "id": 0,
        "name": "some link name",
        "nepk": some pk
        "tuple": 0
      }]
    }
    '''
    ne_object = get_object_or_404(NamedEntity, pk=nepk)
    result = {}
    result['name'] = ne_object.name

    nodes = {}
    links = []
    def linkedNEOfNE(obj, obj_group):
        if obj.pk not in nodes:
            nodes[obj.pk] = {
                "name": obj.name,
                "nepk": obj.pk,
                "group": obj_group,
                "ne_obj": obj
            }
        for tuple in obj.infoboxtuple_set.all():
            def handle_links(match):
                schema = match.group(1)
                link = match.group(2)
                if schema == 'link':
                    real_url = 'http://baike.baidu.com' + link

                    # we are currently unable to resolve duplicate bdbk_urls, so...
                    ne = NamedEntity.objects.exclude(pk=obj.pk).filter(bdbk_url=real_url)
                    if len(ne) > 0:
                        ne = ne[0]
                        if ne.pk not in nodes:
                            nodes[ne.pk] = {
                                "name": ne.name,
                                "nepk": ne.pk,
                                "group": obj_group+1,
                                "ne_obj": ne
                            }

                        links.append({
                            "source": obj.pk,
                            "target": ne.pk
                        })
                    else:
                        pass

                return match.group(3)

            re.sub(r'\{\{([a-zA-Z_]+):([^|]+)\|(.*?)\}\}', handle_links, tuple.content)

            for link in tuple.infoboxtuplelink_set.all():
                match = re.match(r'\{\{([a-zA-Z_]+):(\d+)\}\}', link.linkcontent)
                if not match:
                    continue

                schema = match.group(1)
                mid = match.group(2)
                ne_obj = None

                if schema == 'alias_id':
                    try:
                        alias = NamedEntityAlias.objects.get(pk=mid)
                        ne_obj = alias.link_to
                    except ObjectDoesNotExist as e:
                        pass
                elif schema == 'ne_id':
                    try:
                        ne_obj = NamedEntity.objects.get(pk=mid)
                    except ObjectDoesNotExist as e:
                        pass

                if ne_obj:
                    if ne_obj.pk not in nodes:
                        nodes[ne_obj.pk] = {
                            "name": ne_obj.name,
                            "nepk": ne_obj.pk,
                            "group": obj_group+1,
                            "ne_obj": ne_obj
                        }
                    links.append({
                        "source": obj.pk,
                        "target": ne_obj.pk,
                    })


    linkedNEOfNE(ne_object, 5)
    for i in nodes.values():
        if i['ne_obj'].pk != ne_object.pk:
            linkedNEOfNE(i['ne_obj'], 6)

    # relink all nodes
    new_nodes = []
    new_links = []
    new_neid_nodeid_map = {}

    def addNode(pk):
        if pk not in new_neid_nodeid_map:
            node = nodes[pk]
            new_nodes.append({
                'name': node['name'],
                'ne_pk': node['nepk'],
                'group': node['group'],
            })
            new_neid_nodeid_map[pk] = len(new_nodes) - 1
        return new_neid_nodeid_map[pk]

    addNode(ne_object.pk)

    for link in links:
        source = addNode(link['source'])
        target = addNode(link['target'])
        new_links.append({
            'source': source,
            'target': target
        })
    result['nodes'] = new_nodes
    result['links'] = new_links

    return HttpResponse(json.dumps(result), content_type='text/json')

def qaQueryAPI(request):
    text = request.POST.get('text', None)

    if text is None:
        return HttpResponseBadRequest()

    words = list(jieba.cut(text, cut_all=False))

    ne_result = []

    def search_ne():
        for i in range(len(words)):
            for j in range(i+1, len(words)+1):
                s = ''.join(words[i:j])
                if is_in_stopwords(s):
                    continue

                for o in NamedEntity.objects.filter(name__iexact=s):
                    ne_result.append({
                        'pos': (i,j),
                        'type': 'ne',
                        'display': o.name,
                        'o': o
                    })
                for o in NamedEntity.objects.filter(~Q(name__iexact=s),
                                                    Q(search_term__iexact=s)):
                    ne_result.append({
                        'pos': (i,j),
                        'type': 'ne_search_term',
                        'display': o.search_term,
                        'o': o
                    })
                for o in NamedEntityAlias.objects.filter(link_from__iexact=s):
                    ne_result.append({
                        'pos': (i,j),
                        'type': 'alias',
                        'display': o.link_from,
                        'o': o
                    })

    verb_result = []
    def search_verb():
        for i in range(len(words)):
            for j in range(i+1, len(words)+1):
                s = ''.join(words[i:j])
                try:
                    o = Verb.objects.get(name__iexact=s)
                    verb_result.append({
                        'pos': (i,j),
                        'display': o.name,
                        'o': o
                    })
                except ObjectDoesNotExist as e:
                    pass

    search_ne()
    search_verb()

    result = {
        'tokenize': words,
        'result': []
    }

    named_entities = []
    for i in ne_result:
        if i['type'] == 'alias':
            named_entities.append({
                'ne_title': i['o'].link_to.name,
                'ne_display': i['display'],
                'is_alias': True,
                'ne_id': i['o'].link_to.pk
            })
        else:
            named_entities.append({
                'ne_title': i['o'].name,
                'ne_display': i['display'],
                'ne_id': i['o'].pk,
                'is_alias': False
            })
    result['named_entities'] = sorted(named_entities,
                                      key=lambda x:len(x['ne_display']),
                                      reverse=True)

    for i in ne_result:
        for j in verb_result:
            if i['pos'][1] > j['pos'][0]:
                continue

            ne_obj = i['o'] if i['type'] != 'alias' else i['o'].link_to
            verb_obj = j['o']

            infobox = InfoboxTuple.objects.filter(named_entity=ne_obj.pk,
                                                  verb=verb_obj.pk)
            if len(infobox):
                result['result'].append({
                    'ne_title': ne_obj.name,
                    'ne_display': i['display'],
                    'is_alias': i['type'] == 'alias',
                    'verb': verb_obj.name,
                    'ne_id': ne_obj.pk,
                    'content': strip_content_links(infobox[0].content)
                })

    if not result['result']:
        def edit_distance(s1, s2):
            m=len(s1)+1
            n=len(s2)+1

            tbl = {}
            for i in range(m): tbl[i,0]=i
            for j in range(n): tbl[0,j]=j
            for i in range(1, m):
                for j in range(1, n):
                    cost = 0 if s1[i-1] == s2[j-1] else 1
                    tbl[i,j] = min(tbl[i, j-1]+1, tbl[i-1, j]+1, tbl[i-1, j-1]+cost)

            return tbl[i,j]

        # find infobox by applying edit distance
        for i in ne_result:
            remaining = ''.join(words[i['pos'][1]:])
            ne_obj = i['o'] if i['type'] != 'alias' else i['o'].link_to
            matched = []
            for j in ne_obj.infoboxtuple_set.all():
                verb = j.verb.name

                common_chr = set(remaining) & set(verb)
                if not common_chr:
                    continue

                matched.append((len(common_chr), j))
            matched = sorted(matched, key=lambda x:x[0], reverse=True)
            if matched:
                result['result'].append({
                    'ne_title': ne_obj.name,
                    'ne_display': i['display'],
                    'is_alias': i['type'] == 'alias',
                    'verb': matched[0][1].verb.name,
                    'ne_id': ne_obj.name,
                    'content': strip_content_links(matched[0][1].content)
                })

    result['result'] = sorted(result['result'],
                              key=lambda x:len(x['ne_display']),
                              reverse=True)

    return HttpResponse(json.dumps(result), content_type='text/json')

def QA(request):
    return render(request, 'bdbk/QA.html', {})
