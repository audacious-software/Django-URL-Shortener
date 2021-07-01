from django.conf.urls import url

from .views import url_tracker, create_link_page, create_link, fetch_links_json

urlpatterns = [
    url(r'^fetch.json$', fetch_links_json, name='url_tracker_fetch_links_json'),
    url(r'^create.json$', create_link, name='url_tracker_create_link'),
    url(r'^create$', create_link_page, name='url_tracker_create_link_page'),
    url(r'^(?P<tracking_code>.+)$', url_tracker, name='url_tracker'),
]
