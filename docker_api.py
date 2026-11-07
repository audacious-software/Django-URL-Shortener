# pylint: disable=line-too-long, no-member

import json

import iso8601

from django.contrib import messages
from django.core import serializers

from .models import APIClient, Link, LinkVisit

def import_objects(file_type, import_file): # pylint: disable=too-many-branches
    if file_type in ('url_shortener.apiclient', 'url_shortener.link'):
        user_messages = []

        with import_file.open() as file_stream:
            import_json = json.load(file_stream)

            clients_imported = 0
            links_imported = 0
            visits_imported = 0

            for item_json in import_json: # pylint: disable=too-many-nested-blocks
                if item_json.get('model', None) == 'url_shortener.apiclient':
                    api_client_obj = APIClient()

                    for field_key in item_json.get('fields', {}).keys():
                        field_value = item_json.get('fields', {}).get(field_key, None)

                        setattr(api_client_obj, field_key, field_value)

                    api_client_obj.save()

                    clients_imported += 1
                elif item_json.get('model', None) == 'url_shortener.link':
                    link_obj = Link()

                    for field_key in item_json.get('fields', {}).keys():
                        field_value = item_json.get('fields', {}).get(field_key, None)

                        if field_key in ('created', 'last_click'):
                            if field_value is not None:
                                field_value = iso8601.parse_date(field_value)

                        setattr(link_obj, field_key, field_value)

                    link_obj.save()

                    links_imported += 1

                    for visit in item_json.get('visits', []):
                        if visit.get('model', None) == 'url_shortener.linkvisit':
                            visit_obj = LinkVisit(link=link_obj)

                            for field_key in visit.get('fields', {}).keys():
                                field_value = visit.get('fields', {}).get(field_key, None)

                                if field_key == 'visited':
                                    if field_value is not None:
                                        field_value = iso8601.parse_date(field_value)

                                setattr(visit_obj, field_key, field_value)

                            visit_obj.save()

                            visits_imported += 1

            if clients_imported > 1:
                user_messages.append(('%s API clients imported.' % clients_imported, messages.SUCCESS))
            elif clients_imported == 1:
                user_messages.append(('1 API client imported.', messages.SUCCESS))
            else:
                user_messages.append(('No API clients imported.', messages.INFO))

            if links_imported > 1:
                user_messages.append(('%s links imported.' % links_imported, messages.SUCCESS))
            elif links_imported == 1:
                user_messages.append(('1 link imported.', messages.SUCCESS))
            else:
                user_messages.append(('No links imported.', messages.INFO))

            if visits_imported > 1:
                user_messages.append(('%s link visits imported.' % visits_imported, messages.SUCCESS))
            elif visits_imported == 1:
                user_messages.append(('1 link visit imported.', messages.SUCCESS))
            else:
                user_messages.append(('No link visits imported.', messages.INFO))

        return user_messages

    return None

def export_objects(queryset, queryset_name):
    to_export = []

    if queryset_name == 'APIClient':
        for api_client in queryset:
            api_client_json = json.loads(serializers.serialize('json', APIClient.objects.filter(pk=api_client.pk)))[0]

            del api_client_json['pk']

            to_export.append(api_client_json)

            to_export.extend(export_objects(Link.objects.filter(client_id=api_client.client_id), 'Link'))

    elif queryset_name == 'Link':
        for link in queryset:
            link_json = json.loads(serializers.serialize('json', Link.objects.filter(pk=link.pk)))[0]

            del link_json['pk']

            link_json['visits'] = []

            for visit in link.visits.all():
                visit_json = json.loads(serializers.serialize('json', LinkVisit.objects.filter(pk=visit.pk)))[0]

                del visit_json['pk']
                del visit_json['fields']['link']

                link_json['visits'].append(visit_json)

            to_export.append(link_json)

    return to_export
