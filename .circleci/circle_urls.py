import sys

import django

if sys.version_info[0] > 2:
    from django.urls import re_path as url, include # pylint: disable=no-name-in-module
else:
    from django.conf.urls import url, include

from django.contrib import admin

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^docker/', include('docker_utils.urls')),
    url(r'^u/', include('url_shortener.urls')),
]
