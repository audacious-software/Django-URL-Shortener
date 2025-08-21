# -*- coding: utf-8 -*-

from django.contrib import admin

from .models import Link, LinkVisit, APIClient

class LinkVisitInline(admin.TabularInline):
    model = LinkVisit

    fields = ['link', 'visited', 'user_agent']
    readonly_fields = ['link', 'visited', 'user_agent']

    def has_add_permission(self, request, obj=None): # pylint: disable=arguments-differ,unused-argument
        return False

    def has_delete_permission(self, request, obj=None):
        return False

@admin.register(Link)
class LinkAdmin(admin.ModelAdmin):
    list_display = ('tracking_code', 'original_url', 'external_url', 'last_click', 'created', 'client_id',)
    search_fields = ('tracking_code', 'original_url', 'external_url', 'client_id', 'metadata',)
    list_filter = ('last_click', 'created', 'client_id',)

    inlines = [
        LinkVisitInline,
    ]

@admin.register(LinkVisit)
class LinkVisitAdmin(admin.ModelAdmin):
    list_display = ('link', 'visited', 'user_agent',)
    search_fields = ('link', 'metadata',)
    list_filter = ('visited',)

    readonly_fields = ('link',)

@admin.register(APIClient)
class APIClientAdmin(admin.ModelAdmin):
    list_display = ('contact_email', 'client_id',)
    search_fields = ('contact_email', 'client_id',)
