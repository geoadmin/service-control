# Generated by Django 5.0.9 on 2024-10-23 08:19

from django.db import migrations
from django.db import models


class Migration(migrations.Migration):

    dependencies = [
        ('distributions', '0004_alter_attribution_description_it_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='dataset',
            name='_legacy_id',
            field=models.IntegerField(
                blank=True,
                help_text='This field is used to track objects imported from the BOD',
                null=True,
                verbose_name='Legacy ID'
            ),
        ),
        migrations.AlterField(
            model_name='dataset',
            name='slug',
            field=models.SlugField(max_length=100, verbose_name='Slug'),
        ),
        migrations.AddField(
            model_name='attribution',
            name='_legacy_id',
            field=models.IntegerField(
                blank=True,
                help_text='This field is used to track objects imported from the BOD',
                null=True,
                verbose_name='Legacy ID'
            ),
        ),
    ]
