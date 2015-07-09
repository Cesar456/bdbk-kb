from django.conf.urls import patterns, url

urlpatterns = patterns('ui.views',
    url(r'^hello/$', 'hello'),
    url(r'^showTuplesForNamedEntity/(?P<nepk>\d+|random)/$', 'ShowTuplesForNamedEntity', name='ShowTuplesForNamedEntity'),
)
