# pylint: skip-file
# Generated by Django 3.2.25 on 2024-06-03 15:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('url_shortener', '0012_alter_apiclient_options'),
    ]

    operations = [
        migrations.AlterField(
            model_name='apiclient',
            name='contact_email',
            field=models.EmailField(max_length=1024, unique=True, verbose_name='Contact e-mail'),
        ),
    ]
