# pylint: disable=no-member

# -*- coding: utf-8 -*-

import binascii
import json
import random
import string

import nacl

from nacl.signing import VerifyKey

from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.http import Http404, HttpResponseForbidden, JsonResponse
from django.shortcuts import redirect, render
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
                print('URL: ' + str(url))
                print('SIG: ' + str(signature))

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
                new_link.save()

                payload = {
                    'short_url': new_link.fetch_short_url()
                }

                return JsonResponse(payload, json_dumps_params={'indent': 2})
            except nacl.exceptions.BadSignatureError:
                print('BAD KEY: ' + str(client))
                # pass # signature failed

    return HttpResponseForbidden()
