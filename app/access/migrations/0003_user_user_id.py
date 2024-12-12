# Generated by Django 5.0.9 on 2024-11-20 11:44

from utils.short_id import generate_short_id

from django.apps.registry import Apps
from django.db import migrations
from django.db import models
from django.db.backends.base.schema import BaseDatabaseSchemaEditor


def populate_user_id(apps: Apps, schema_editor: BaseDatabaseSchemaEditor) -> None:
    User = apps.get_model('access', 'User')
    for obj in User.objects.all():
        obj.user_id = generate_short_id()
        obj.save()


class Migration(migrations.Migration):

    dependencies = [
        ('access', '0002_user_deleted_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='user_id',
            field=models.CharField(default=generate_short_id, null=True, verbose_name='User ID'),
        ),
        migrations.RunPython(populate_user_id, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='user',
            name='user_id',
            field=models.CharField(default=generate_short_id, unique=True, verbose_name='User ID'),
        ),
    ]