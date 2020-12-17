# -*- coding: utf-8 -*-

from django.contrib import admin

from .models import Link, LinkVisit, APIClient

@admin.register(Link)
class LinkAdmin(admin.ModelAdmin):
    list_display = ('tracking_code', 'original_url', 'external_url', 'created',)
    search_fields = ('tracking_code', 'original_url', 'external_url', 'metadata')
    list_filter = ('created',)

@admin.register(LinkVisit)
class LinkVisitAdmin(admin.ModelAdmin):
    list_display = ('link', 'visited', 'user_agent',)
    search_fields = ('link', 'metadata',)
    list_filter = ('visited',)

@admin.register(APIClient)
class APIClientAdmin(admin.ModelAdmin):
    list_display = ('contact_email', 'client_id',)
    search_fields = ('contact_email', 'client_id',)
