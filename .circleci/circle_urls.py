
import sys

if sys.version_info[0] > 2:
    from django.urls import re_path as url, include, # pylint: disable=no-name-in-module
else:
    from django.conf.urls import url, include

from django.contrib import admin

urlpatterns = [
    url('^admin/', admin.site.urls),
    url('^docker/', include('docker_utils.urls')),
    url('^u/', include('url_shortener.urls')),
]
