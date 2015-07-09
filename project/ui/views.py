import json
import random

from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render

from bdbk.models import InfoboxTuple, NamedEntity, Verb


# Create your views here.
def hello(request):
    return HttpResponse('Hello World')

def ShowTuplesForNamedEntity(request, nepk):
    if nepk == 'random':
        nepk = random.randint(0, NamedEntity.objects.all().count()-1)
        return HttpResponseRedirect(reverse('ShowTuplesForNamedEntity', args=(nepk,)))

    nepk = int(nepk)

    ne_object = get_object_or_404(NamedEntity, pk=nepk)

    tuples = []

    for infoboxtuple in ne_object.infoboxtuple_set.all():
        tuples.append({
            'verb': infoboxtuple.verb.name,
            'content': infoboxtuple.content
        })

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

    # current data status
    total_tuple_count = InfoboxTuple.objects.all().count()
    total_verb_count = Verb.objects.all().count()

    result = {
        'namedentity':{
            'ne_id': nepk,
            'ne_title': ne_object.name,
            'ne_search_term': ne_object.search_term,
            'ne_last_modified': ne_object.last_modified.strftime('%Y-%m-%d %H:%M:%S'),
            'ne_bdbk_url': ne_object.bdbk_url,
            'ne_infobox': tuples
            },
        'randomnes': random_nes,
        'status': {
            'ne_count': total_ne_count,
            'infoboxtuple_count': total_tuple_count,
            'verb_count': total_verb_count
        }
    }

    return render(request, 'ui/ShowTuplesForNamedEntity.html', result)
    return HttpResponse(response_string, content_type='text/json')
