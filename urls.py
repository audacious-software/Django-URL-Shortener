# pylint: disable=wrong-import-position, line-too-long

import sys

if sys.version_info[0] > 2:
    from django.urls import re_path as url # pylint: disable=no-name-in-module
else:
    from django.conf.urls import url

from .views import url_tracker, create_link_page, create_link, fetch_links_json, url_tracker_qr, url_tracker_qr_custom

urlpatterns = [
    url(r'^fetch.json$', fetch_links_json, name='url_tracker_fetch_links_json'),
    url(r'^create.json$', create_link, name='url_tracker_create_link'),
    url(r'^create$', create_link_page, name='url_tracker_create_link_page'),
    url(r'^qr/custom$', url_tracker_qr_custom, name='url_tracker_qr_custom'),
    url(r'^qr/(?P<tracking_code>.+)$', url_tracker_qr, name='url_tracker_qr'),
    url(r'^(?P<tracking_code>.+)$', url_tracker, name='url_tracker'),
]
