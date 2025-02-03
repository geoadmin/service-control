# Generated by Django 5.0.9 on 2025-01-30 14:44

from utils.short_id import generate_short_id

from django.apps.registry import Apps
from django.db import migrations
from django.db import models
from django.db.backends.base.schema import BaseDatabaseSchemaEditor


def populate_external_id(apps: Apps, schema_editor: BaseDatabaseSchemaEditor) -> None:
    Attribution = apps.get_model('distributions', 'Attribution')
    for obj in Attribution.objects.all():
        obj.external_id = generate_short_id()
        obj.save()


class Migration(migrations.Migration):

    dependencies = [
        ('distributions', '0007_packagedistribution'),
    ]

    operations = [
        migrations.AddField(
            model_name='attribution',
            name='external_id',
            field=models.CharField(
                default=generate_short_id,
                help_text=
                "This is the externally visible ID, usually of format 'ch.<acronym>'. In BOD this was tracked in column 'attribution'",
                verbose_name='External ID'
            ),
        ),
        migrations.RunPython(populate_external_id, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='attribution',
            name='external_id',
            field=models.CharField(
                db_index=True,
                unique=True,
                default=generate_short_id,
                help_text=
                "This is the externally visible ID, usually of format 'ch.<acronym>'. In BOD this was tracked in column 'attribution'",
                verbose_name='External ID'
            ),
        ),
    ]
