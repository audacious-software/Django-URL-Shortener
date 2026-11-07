# pylint: disable=line-too-long, ungrouped-imports
# -*- coding: utf-8 -*-

from django.contrib import admin

try:
    from docker_utils.admin import PortableModelAdmin as ModelAdmin
except ImportError:
    from django.contrib.admin import ModelAdmin as ModelAdmin # pylint: disable=useless-import-alias

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
class LinkAdmin(ModelAdmin):
    list_display = ('tracking_code', 'original_url', 'external_url', 'last_click', 'created', 'client_id',)
    search_fields = ('tracking_code', 'original_url', 'external_url', 'client_id', 'metadata',)
    list_filter = ('last_click', 'created', 'client_id',)

    inlines = [
        LinkVisitInline,
    ]

    def export_objects(self, request, queryset):
        return self.portable_model_export_items(request, queryset)

    export_objects.short_description = 'Export selected links'

    actions = [
        'export_objects',
    ]

@admin.register(LinkVisit)
class LinkVisitAdmin(ModelAdmin):
    list_display = ('link', 'visited', 'user_agent',)
    search_fields = ('link', 'metadata',)
    list_filter = ('visited',)

    readonly_fields = ('link',)

@admin.register(APIClient)
class APIClientAdmin(ModelAdmin):
    list_display = ('contact_email', 'client_id',)
    search_fields = ('contact_email', 'client_id',)

    def export_objects(self, request, queryset):
        return self.portable_model_export_items(request, queryset)

    export_objects.short_description = 'Export selected API clients'

    actions = [
        'export_objects',
    ]
