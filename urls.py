from django.conf.urls import include, url

from .views import url_tracker

urlpatterns = [
    url(r'^(?P<tracking_code>.+)/$', url_tracker, name='url_tracker'),
]
