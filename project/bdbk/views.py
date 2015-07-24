import json
import random
import re
import zlib

import pymongo
from bson import objectid
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.utils.html import escape
from django.views.decorators.http import require_http_methods

from .models import InfoboxTuple, NamedEntity, Verb, DBVersion


def resolve_content_links(content):
    # TODO: add cache
    content = escape(content)

    def replaced_content(mch):
        linked_url_real = 'http://baike.baidu.com' + mch.group(1)
        linked_ne = NamedEntity.objects.filter(bdbk_url=linked_url_real)
        # TODO: how to map the linked named entity more properly
        if len(linked_ne):
            linked_ne_url = reverse('ShowTuplesForNamedEntity', args=(linked_ne[0].pk,))
            return '<a href="%s">%s</a>' % (linked_ne_url, mch.group(2))
        else:
            return mch.group(2)

    return re.sub(r'\{\{link:([^|]+)\|(.*?)\}\}', replaced_content, content)

def populate_db_status():
    # current data status
    total_tuple_count = InfoboxTuple.objects.all().count()
    total_verb_count = Verb.objects.all().count()
    total_ne_count = NamedEntity.objects.all().count()

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
    total_ne_count = NamedEntity.objects.all().count()
    random_nes = []
    random_count = min(6, total_ne_count)
    for i in range(0, random_count):
        random_index = random.randint(0, total_ne_count-1)
        randomed = NamedEntity.objects.all()[random_index]

        random_nes.append({
            'ne_title': randomed.name,
            'ne_url': reverse('ShowTuplesForNamedEntity', args=(randomed.pk,))
        })

    return {
        'randomnes': random_nes
    }

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

        qdict = {}
        friendly_name = []
        if ne_str:
            friendly_name_1, qdict_1 = action_to_query_dict('named_entity__name', 'Name of entity', ne_action, ne_str)
            qdict.update(qdict_1)
            friendly_name.append(friendly_name_1)
        if verb_str:
            friendly_name_2, qdict_2 = action_to_query_dict('verb__name', 'verb', verb_action, verb_str)
            qdict.update(qdict_2)
            friendly_name.append(friendly_name_2)
        if content_str:
            friendly_name_3, qdict_3 = action_to_query_dict('content', 'attribute value', content_action, content_str)
            qdict.update(qdict_3)
            friendly_name.append(friendly_name_3)

        if not qdict:
            context = {
                'search_result_message': 'No filter applied.'
            }
        else:
            # TODO: paginator
            qresult = InfoboxTuple.objects.filter(**qdict).order_by('named_entity', 'verb')

            result = []
            for i in qresult:
                result.append({
                    'namedentity': i.named_entity.name,
                    'namedentity_url': reverse('ShowTuplesForNamedEntity', args=(i.named_entity.id,)),
                    'verb': i.verb.name,
                    'content': resolve_content_links(i.content)
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
            'content': resolve_content_links(obj.content),
        })

    result = {
        'search_term': search_term,
        'search_result_ne': search_result_ne,
        'search_result_content': search_result_content,
    }
    return render(request, 'bdbk/SearchResult.html', result)

def ShowTuplesForNamedEntity(request, nepk):
    if nepk == 'random':
        nepk_index = random.randint(0, NamedEntity.objects.all().count()-1)
        random_ne = NamedEntity.objects.all()[nepk_index]
        nepk = random_ne.pk
        return HttpResponseRedirect(reverse('ShowTuplesForNamedEntity', args=(nepk,)))

    nepk = int(nepk)

    ne_object = get_object_or_404(NamedEntity, pk=nepk)

    tuples = []

    for infoboxtuple in ne_object.infoboxtuple_set.all():
        tuples.append({
            'verb': infoboxtuple.verb.name,
            'content': resolve_content_links(infoboxtuple.content),
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
                    try:
                        ne = NamedEntity.objects.exclude(pk=obj.pk).get(bdbk_url=real_url)
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
                    except ObjectDoesNotExist as e:
                        pass

                return match.group(3)

            print obj.pk, tuple.pk
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
    for nodeid, node in nodes.items():
        new_nodes.append({
            'name': node['name'],
            'ne_pk': node['nepk'],
            'group': node['group'],
        })
        new_neid_nodeid_map[nodeid] = len(new_nodes) - 1

    for link in links:
        source = new_neid_nodeid_map[link['source']]
        target = new_neid_nodeid_map[link['target']]
        new_links.append({
            'source': source,
            'target': target
        })
    result['nodes'] = new_nodes
    result['links'] = new_links

    return HttpResponse(json.dumps(result), content_type='text/json')
