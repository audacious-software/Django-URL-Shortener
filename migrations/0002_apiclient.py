# pylint: skip-file
# Generated by Django 2.2.17 on 2020-12-10 17:50

from django.db import migrations, models
import url_shortener.models


class Migration(migrations.Migration):

    dependencies = [
        ('url_shortener', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='APIClient',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('contact_email', models.EmailField(max_length=1024, unique=True)),
                ('client_id', models.CharField(default=url_shortener.models.generate_client_id, max_length=64, unique=True)),
            ],
        ),
    ]