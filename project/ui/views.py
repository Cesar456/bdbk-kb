import json
import random
import re

from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.utils.html import escape
from django.views.decorators.http import require_http_methods

from bdbk.models import InfoboxTuple, NamedEntity, Verb


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
            'verb_count': total_verb_count
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
def Status_Overview(request):
    return HttpResponse('TODO')

def Status_Verb(request):
    return HttpResponse('TODO')

def Status_NamedEntity(request, filter_string=None):
    return HttpResponse('TODO')

def AdvancedSearch(request):
    def AdvancedSearch_get(request):
        context = {}
        context.update(populate_random_suggestion())
        context.update(populate_db_status())
        return render(request, 'ui/AdvancedSearch_form.html', context)

    def AdvancedSearch_post(request):
        ne_action = request.POST.get('limitNE_action')
        ne_str = request.POST.get('limitNE_str')

        verb_action = request.POST.get('limitVERB_action')
        verb_str = request.POST.get('limitVERB_str')

        content_action = request.POST.get('limitCONTENT_action')
        content_str = request.POST.get('limitCONTENT_str')

        def action_to_query_dict(field, field_friendly_name, action, qstr):
            if action == 'IS':
                a = 'exact'
                b = '%s is "%s"' % (field_friendly_name, qstr)
            elif action == 'STARTSWITH':
                a = 'startswith'
                b = '%s starts with "%s"' % (field_friendly_name, qstr)
            elif action == 'ENDSWITH':
                a = 'endswith'
                b = '%s ends with "%s"' % (field_friendly_name, qstr)
            elif action == 'CONTAINS':
                a = 'contains'
                b = '%s contains "%s"' % (field_friendly_name, qstr)
            else:
                a = 'contains'
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
                    'verb': i.verb.name,
                    'content': resolve_content_links(i.content)
                })

            context = {
                'search_result': result,
                'friendly_query_string': ', '.join(friendly_name),
                'search_result_message': '%d results.' % len(result)
            }

        context.update(populate_db_status())
        return render(request, 'ui/AdvancedSearch_result.html', context)

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
    ne_search_result = NamedEntity.objects.filter(name__contains=search_term)

    search_result_ne = []
    for obj in ne_search_result:
        search_result_ne.append({
            'ne_name': obj.name,
            'ne_url': reverse('ShowTuplesForNamedEntity', args=(obj.pk,))
        })

    tuple_search_result = InfoboxTuple.objects.filter(content__contains=search_term)

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
    return render(request, 'ui/SearchResult.html', result)

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

    result = {
        'namedentity':{
            'ne_id': nepk,
            'ne_title': ne_object.name,
            'ne_search_term': ne_object.search_term,
            'ne_last_modified': ne_object.last_modified.strftime('%Y-%m-%d %H:%M:%S') if ne_object.last_modified else 'Not Specified',
            'ne_bdbk_url': ne_object.bdbk_url,
            'ne_infobox': tuples
            },
    }
    result.update(populate_random_suggestion())
    result.update(populate_db_status())

    return render(request, 'ui/ShowTuplesForNamedEntity.html', result)
