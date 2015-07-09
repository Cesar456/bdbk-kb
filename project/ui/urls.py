from django.conf.urls import patterns, url

urlpatterns = patterns('ui.views',
    url(r'^showTuplesForNamedEntity/(?P<nepk>\d+|random)/$', 'ShowTuplesForNamedEntity', name='ShowTuplesForNamedEntity'),
    url(r'^fuzzySearch/', 'FuzzySearch', name='FuzzySearch')
)
