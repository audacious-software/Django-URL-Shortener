import json

from django.db import models

from django.conf import settings
from django.urls import reverse

class Link(models.Model):
    tracking_code = models.CharField(max_length=32, unique=True)
    original_url = models.URLField(max_length=4096)
    created = models.DateTimeField(auto_now_add=True)
    external_url = models.URLField(max_length=4096)

    metadata = models.TextField(max_length=1048576, default='{}')

    def __str__(self):
        return str(self.original_url)

    def get_absolute_url(self):
        return settings.URL_TRACKER_PREFIX + reverse('url_tracker', args=[self.tracking_code])

    def fetch_short_url(self):
        if self.external_url is None:
            self.external_url = self.get_absolute_url()
            self.save()

        return self.external_url

    def log_visit(self, request):
        visit = LinkVisit(link=self)

        visit.user_agent = request.META['HTTP_USER_AGENT']

        metadata = {}

        for key in request.META:
            if key.startswith('wsgi.'):
                pass
            elif key.startswith('mod_wsgi.'):
                pass
            else:
                metadata[key] = str(request.META[key])

        visit.metadata = json.dumps(metadata, indent=2)

        visit.save()

class LinkVisit(models.Model):
    link = models.ForeignKey(Link, related_name='visits', on_delete=models.CASCADE)

    visited = models.DateTimeField(auto_now_add=True)

    user_agent = models.CharField(max_length=4096, null=True, blank=True)

    metadata = models.TextField(max_length=1048576, default='{}')
