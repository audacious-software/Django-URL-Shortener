# pylint: skip-file
# Generated by Django 3.2.25 on 2024-06-03 15:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('url_shortener', '0006_alter_link_client_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='apiclient',
            name='query_window_days',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
