from django.conf.urls import patterns, url

urlpatterns = patterns('ui.views',
    url(r'^QA/$', 'QA', name='QA'),
)
