# pylint: disable=line-too-long, no-member

import json
import random
import string

from nacl.encoding import HexEncoder
from nacl.signing import SigningKey, VerifyKey

from django.conf import settings
from django.db import models
from django.dispatch import receiver
from django.urls import reverse

class Link(models.Model):
    tracking_code = models.CharField(max_length=32, unique=True)
    original_url = models.URLField(max_length=4096, verbose_name='Original URL')
    created = models.DateTimeField(auto_now_add=True)
    external_url = models.URLField(max_length=4096, verbose_name='External URL')

    metadata = models.TextField(max_length=1048576, default='{}')

    client_id = models.CharField(max_length=4096, null=True, blank=True, db_index=True, verbose_name='Client ID')

    last_click = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return str(self.original_url) + ' (' + self.tracking_code + ')'

    def fetch_client_id(self):
        if self.client_id is not None:
            return self.client_id

        metadata = json.loads(self.metadata)

        client_id = metadata.get('api_client', None)

        if client_id is not None:
            self.client_id = client_id

            self.save()

        return self.client_id

    def get_absolute_url(self):
        return settings.URL_TRACKER_PREFIX + reverse('url_tracker', args=[self.tracking_code])

    def fetch_short_url(self):
        if self.external_url is None or self.external_url.strip() == '':
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

@receiver(models.signals.pre_save, sender=Link)
def add_tracking_code_if_needed(sender, instance, *args, **kwargs): # pylint: disable=unused-argument
    tracking_code = instance.tracking_code

    is_random = False

    tracking_code_base = tracking_code
    tracking_code_base_index = 1

    if tracking_code is None or tracking_code.strip() == '':
        tracking_code = ''.join(random.SystemRandom().choice(string.ascii_lowercase + string.digits) for _ in range(8))

        is_random = True

    while Link.objects.filter(tracking_code=tracking_code).count() > 1:
        if is_random:
            tracking_code = ''.join(random.SystemRandom().choice(string.ascii_lowercase + string.digits) for _ in range(8))
        else:
            tracking_code = tracking_code_base + '-' + str(tracking_code_base_index)

        tracking_code_base_index += 1

    instance.tracking_code = tracking_code


class LinkVisit(models.Model):
    link = models.ForeignKey(Link, related_name='visits', on_delete=models.CASCADE)

    visited = models.DateTimeField(auto_now_add=True)

    user_agent = models.CharField(max_length=4096, null=True, blank=True)

    metadata = models.TextField(max_length=1048576, default='{}')


def generate_client_id(length=64):
    identifier = None

    while identifier is None or APIClient.objects.filter(client_id=identifier).count() > 0:
        identifier = ''.join(random.SystemRandom().choice(string.ascii_lowercase + string.digits) for _ in range(length))

    return identifier


class APIClient(models.Model):
    class Meta: # pylint: disable=too-few-public-methods, no-init, old-style-class
        verbose_name = 'API client'

    contact_email = models.EmailField(max_length=1024, unique=True, verbose_name='Contact e-mail')
    client_id = models.CharField(max_length=64, unique=True, default=generate_client_id, verbose_name='Client ID')

    signing_key = models.CharField(max_length=1024, null=True, blank=True)
    verification_key = models.CharField(max_length=1024, null=True, blank=True)

    query_window_days = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return str(self.contact_email)

    def generate_keys(self):
        if self.signing_key is None or self.signing_key == '':
            signing_key = SigningKey.generate()

            self.signing_key = signing_key.encode(encoder=HexEncoder).decode('utf8')
            self.verification_key = signing_key.verify_key.encode(encoder=HexEncoder).decode('utf8')

            self.save()

    def fetch_verification_key(self, hex_format=True):
        if self.verification_key is None or self.verification_key.strip() == '':
            self.generate_keys()

        if hex_format:
            return self.verification_key

        return VerifyKey(self.verification_key, encoder=HexEncoder)

    def fetch_signing_key(self, hex_format=True):
        if self.signing_key is None or self.signing_key.strip() == '':
            self.generate_keys()

        if hex_format:
            return self.signing_key

        return SigningKey(self.signing_key, encoder=HexEncoder)

@receiver(models.signals.post_save, sender=APIClient)
def add_keys_if_needed(sender, instance, created, **kwargs): # pylint: disable=unused-argument
    instance.generate_keys()
