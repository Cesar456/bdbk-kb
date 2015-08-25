from django.conf.urls import patterns, url
from django.views.generic.base import RedirectView

urlpatterns = patterns('bdbk.views',
    url(r'^$', RedirectView.as_view(url='qa/', permanent=False)),
    url(r'^showTuplesForNamedEntity/(?P<nepk>\d+|random)/$', 'ShowTuplesForNamedEntity', name='ShowTuplesForNamedEntity'),
    url(r'^fuzzySearch/$', 'FuzzySearch', name='FuzzySearch'),
    url(r'^qa/$', 'QA', name='QA'),
    url(r'^status/namedEntity/(?P<filter_string>[^/]+)/$', 'Status_NamedEntity', name='Status_NamedEntity'),
    url(r'^status/namedEntity/$', 'Status_NamedEntity', name='Status_NamedEntity'),
    url(r'^status/verb/$', 'Status_Verb', name='Status_Verb'),
    url(r'^status/overview/$', 'Status_Overview', name='Status_Overview'),
    url(r'^advancedSearch/$', 'AdvancedSearch', name='AdvancedSearch'),

    url(r'^about/$', 'About', name='About'),

    # json API
    url(r'^graph/namedEntityLinks/(?P<nepk>\d+)/$', 'namedEntityLinks', name='namedEntityLinks'),
    url(r'^qa/query/$', 'qaQueryAPI', name='qaQueryAPI'),
    url(r'^qa/hints/$', 'qaHints', name='qaHints'),
)
