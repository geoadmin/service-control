# Generated by Django 5.0.9 on 2024-09-11 14:49

from django.db import migrations
from django.db import models


class Migration(migrations.Migration):

    dependencies = [
        ('provider', '0003_provider_acronym_rm_provider_name_rm'),
    ]

    operations = [
        migrations.AlterField(
            model_name='provider',
            name='acronym_de',
            field=models.CharField(verbose_name='Acronym (German)'),
        ),
        migrations.AlterField(
            model_name='provider',
            name='acronym_en',
            field=models.CharField(verbose_name='Acronym (English)'),
        ),
        migrations.AlterField(
            model_name='provider',
            name='acronym_fr',
            field=models.CharField(verbose_name='Acronym (French)'),
        ),
        migrations.AlterField(
            model_name='provider',
            name='name_de',
            field=models.CharField(verbose_name='Name (German)'),
        ),
        migrations.AlterField(
            model_name='provider',
            name='name_en',
            field=models.CharField(verbose_name='Name (English)'),
        ),
        migrations.AlterField(
            model_name='provider',
            name='name_fr',
            field=models.CharField(verbose_name='Name (French)'),
        ),
    ]