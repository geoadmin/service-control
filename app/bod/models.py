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

    class Meta:
        managed = settings.TESTING
        db_table = 'contactorganisation'
