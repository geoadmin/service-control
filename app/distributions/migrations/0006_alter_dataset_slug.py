# Generated by Django 5.0.9 on 2024-11-27 06:48

import utils.fields

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('distributions', '0005_dataset__legacy_id_alter_dataset_slug_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dataset',
            name='slug',
            field=utils.fields.CustomSlugField(max_length=100, verbose_name='Slug'),
        ),
    ]
