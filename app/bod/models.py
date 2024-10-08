from django.conf import settings
from django.db import models


class BodContactOrganisation(models.Model):
    pk_contactorganisation_id = models.AutoField(primary_key=True)

    abkuerzung_de = models.CharField(max_length=255, blank=True, null=True)
    abkuerzung_fr = models.CharField(max_length=255, blank=True, null=True)
    abkuerzung_en = models.CharField(max_length=255, blank=True, null=True)
    abkuerzung_it = models.CharField(max_length=255, blank=True, null=True)
    abkuerzung_rm = models.CharField(max_length=255, blank=True, null=True)

    name_de = models.CharField(max_length=255, blank=True, null=True)
    name_fr = models.CharField(max_length=255, blank=True, null=True)
    name_en = models.CharField(max_length=255, blank=True, null=True)
    name_it = models.CharField(max_length=255, blank=True, null=True)
    name_rm = models.CharField(max_length=255, blank=True, null=True)

    attribution = models.TextField(blank=True, null=True)

    class Meta:
        managed = settings.TESTING
        db_table = 'contactorganisation'


class BodDataset(models.Model):
    id = models.AutoField(unique=True, primary_key=True)
    id_dataset = models.TextField()
    fk_contactorganisation_id = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = settings.TESTING
        db_table = 'dataset'


class BodTranslations(models.Model):
    msg_id = models.CharField(primary_key=True, max_length=255)

    de = models.CharField(max_length=5000, blank=True, null=True)
    fr = models.CharField(max_length=5000, blank=True, null=True)
    it = models.CharField(max_length=5000, blank=True, null=True)
    rm = models.CharField(max_length=5000, blank=True, null=True)
    en = models.CharField(max_length=5000, blank=True, null=True)

    class Meta:
        managed = settings.TESTING
        db_table = 'translations'
