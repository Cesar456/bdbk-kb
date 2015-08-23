from django.conf.urls import include, url
from django.views.generic.base import RedirectView

urlpatterns = [
    url(r'^$', RedirectView.as_view(url='bdbk/', permanent=False)),
    url(r'^bdbk/', include('bdbk.urls')),
]
