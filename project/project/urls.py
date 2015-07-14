from django.conf.urls import include, url

urlpatterns = [
    url(r'^bdbk/', include('bdbk.urls')),
    url(r'^ui/', include('ui.urls')),
]
