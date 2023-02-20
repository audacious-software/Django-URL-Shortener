# pylint: disable=no-member

# -*- coding: utf-8 -*-

import binascii
import datetime
import json
import random
import string

import nacl

from nacl.signing import VerifyKey

from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.http import Http404, HttpResponseForbidden, JsonResponse
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from .models import Link, APIClient

def url_tracker(request, tracking_code):
    link = Link.objects.filter(tracking_code=tracking_code).first()

    if link is not None:
        link.log_visit(request)

        return redirect(link.original_url)

    raise Http404

@staff_member_required
def create_link_page(request):
    context = {}

    return render(request, "url_shortener_create_link_page.html", context)

@csrf_exempt
def create_link(request):
    if request.method == 'POST':
        url = request.POST.get('url')
        signature = binascii.unhexlify(request.POST.get('signature'))

        for client in APIClient.objects.all():
            verify_key = VerifyKey(binascii.unhexlify(client.verification_key))

            try:
                verify_key.verify(url.encode('utf8'), signature)

                # Signature passed

                metadata = {}

                for key in request.POST.keys():
                    metadata[key] = request.POST.get(key)

                del metadata['url']
                del metadata['signature']

                metadata['api_client'] = client.client_id

                for link in Link.objects.filter(original_url=url):
                    link_metadata = json.loads(link.metadata)

                    if link_metadata == metadata:
                        payload = {
                            'short_url': link.fetch_short_url()
                        }

                        return JsonResponse(payload, json_dumps_params={'indent': 2})

                tracking_code = None

                if 'tracking_code' in request.POST:
                    tracking_core = request.POST.get('tracking_code')

                    tracking_code = tracking_core
                    code_index = 0

                    while Link.objects.filter(tracking_code=tracking_code).count() > 0:
                        code_index += 1

                        tracking_code = tracking_core + '-' + str(code_index)
                else:
                    tracking_code = ''.join(random.SystemRandom().choice(string.ascii_lowercase + string.digits) for _ in range(settings.URL_SHORTENER_CODE_LENGTH))

                    while Link.objects.filter(tracking_code=tracking_code).count() > 0:
                        tracking_code = ''.join(random.SystemRandom().choice(string.ascii_lowercase + string.digits) for _ in range(settings.URL_SHORTENER_CODE_LENGTH))

                new_link = Link(original_url=url, tracking_code=tracking_code)
                new_link.metadata = json.dumps(metadata, indent=2)

                new_link.save()

                payload = {
                    'short_url': new_link.fetch_short_url()
                }

                return JsonResponse(payload, json_dumps_params={'indent': 2})
            except nacl.exceptions.BadSignatureError:
                pass # signature failed

    return HttpResponseForbidden()

@csrf_exempt
def fetch_links_json(request):
    if request.method == 'POST': # pylint: disable=too-many-nested-blocks
        signature = binascii.unhexlify(request.POST.get('signature'))

        for client in APIClient.objects.all():
            verify_key = VerifyKey(binascii.unhexlify(client.verification_key))

            now = timezone.now()

            for i in range(0, 5):
                for j in [-1, 1]:
                    signature_value = (now + datetime.timedelta(minutes=(i * j))).isoformat()[:16] # pylint: disable=superfluous-parens

                    try:
                        verify_key.verify(signature_value.encode('utf8'), signature)

                        payload = []

                        for link in Link.objects.filter(metadata__icontains=client.client_id).order_by('-pk'):
                            metadata = json.loads(link.metadata)

                            link_payload = {
                                'original': link.original_url,
                                'short_url': link.fetch_short_url(),
                                'created': link.created.isoformat(),
                                'visits': [],
                                'client_metadata': metadata.get('client_metadata', '')
                            }

                            for visit in link.visits.order_by('-visited'):
                                link_payload['visits'].append({
                                    'visited': visit.visited.isoformat(),
                                    'user_agent': visit.user_agent
                                })

                            payload.append(link_payload)

                        return JsonResponse(payload, safe=False, json_dumps_params={'indent': 2})
                    except nacl.exceptions.BadSignatureError:
                        pass # signature failed

    return HttpResponseForbidden()
