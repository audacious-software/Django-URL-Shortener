# pylint: disable=no-member

# -*- coding: utf-8 -*-


from django.http import Http404
from django.shortcuts import redirect

from .models import Link

def url_tracker(request, tracking_code):
    link = Link.objects.filter(tracking_code=tracking_code).first()

    if link is not None:
        link.log_visit(request)

        return redirect(link.original_url)

    raise Http404
