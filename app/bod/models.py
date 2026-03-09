from django.conf import settings
from django.contrib.postgres.fields import ArrayField
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
        db_table = "contactorganisation"


class BodDataset(models.Model):
    id = models.AutoField(unique=True, primary_key=True)
    id_dataset = models.TextField()
    fk_geocat = models.TextField()
    fk_contactorganisation_id = models.IntegerField(blank=True, null=True)
    staging = models.TextField(blank=True, null=True)

    class Meta:
        managed = settings.TESTING
        db_table = "dataset"


class BodTranslations(models.Model):
    msg_id = models.CharField(primary_key=True, max_length=255)

    de = models.CharField(max_length=5000, blank=True, null=True)
    fr = models.CharField(max_length=5000, blank=True, null=True)
    it = models.CharField(max_length=5000, blank=True, null=True)
    rm = models.CharField(max_length=5000, blank=True, null=True)
    en = models.CharField(max_length=5000, blank=True, null=True)

    class Meta:
        managed = settings.TESTING
        db_table = "translations"


class BodGeocatPublish(models.Model):
    bgdi_id = models.AutoField(unique=True, primary_key=True)
    fk_id_dataset = models.TextField()

    bezeichnung_de = models.CharField(max_length=5000, blank=True, null=True)
    bezeichnung_fr = models.CharField(max_length=5000, blank=True, null=True)
    bezeichnung_it = models.CharField(max_length=5000, blank=True, null=True)
    bezeichnung_rm = models.CharField(max_length=5000, blank=True, null=True)
    bezeichnung_en = models.CharField(max_length=5000, blank=True, null=True)

    abstract_de = models.CharField(max_length=5000, blank=True, null=True)
    abstract_fr = models.CharField(max_length=5000, blank=True, null=True)
    abstract_it = models.CharField(max_length=5000, blank=True, null=True)
    abstract_rm = models.CharField(max_length=5000, blank=True, null=True)
    abstract_en = models.CharField(max_length=5000, blank=True, null=True)

    class Meta:
        managed = settings.TESTING
        db_table = "geocat_publish"


class BodLayersJS(models.Model):
    bgdi_id = models.AutoField(unique=True, primary_key=True)

    layer_id = models.CharField(max_length=5000, null=True, blank=True)
    bod_layer_id = models.CharField(max_length=5000, null=True, blank=True)
    topics = models.CharField(max_length=5000, null=True, blank=True)
    chargeable = models.BooleanField()
    staging = models.CharField(max_length=5000, null=True, blank=True)
    server_layername = models.CharField(max_length=5000, null=True, blank=True)
    attribution = models.CharField(max_length=5000, null=True, blank=True)
    layertype = models.CharField(max_length=5000, null=True, blank=True)
    opacity = models.FloatField(null=True, blank=True)
    minresolution = models.FloatField(null=True, blank=True)
    maxresolution = models.FloatField(null=True, blank=True)
    extent = ArrayField(models.FloatField(null=True, blank=True), blank=True)
    backgroundlayer = models.BooleanField()
    tooltip = models.BooleanField()
    searchable = models.BooleanField()
    timeenabled = models.BooleanField()
    haslegend = models.BooleanField()
    singletile = models.BooleanField()
    highlightable = models.BooleanField()
    wms_layers = models.CharField(max_length=5000, null=True, blank=True)
    time_behaviour = models.CharField(max_length=5000, null=True, blank=True)
    image_format = models.CharField(max_length=5000, null=True, blank=True)
    tilematrix_resolution_max = models.FloatField(null=True, blank=True)
    timestamps = ArrayField(models.CharField(max_length=5000, null=True, blank=True))
    parentlayerid = models.CharField(max_length=5000, null=True, blank=True)
    sublayersids = ArrayField(models.CharField(max_length=5000, null=True, blank=True))
    time_get_parameter = models.CharField(max_length=5000, null=True, blank=True)
    time_format = models.CharField(max_length=5000, null=True, blank=True)
    wms_gutter = models.IntegerField(null=True, blank=True)
    sphinx_index = models.CharField(max_length=5000, null=True, blank=True)
    geojson_url_de = models.CharField(max_length=5000, null=True, blank=True)
    geojson_url_fr = models.CharField(max_length=5000, null=True, blank=True)
    geojson_url_it = models.CharField(max_length=5000, null=True, blank=True)
    geojson_url_en = models.CharField(max_length=5000, null=True, blank=True)
    geojson_url_rm = models.CharField(max_length=5000, null=True, blank=True)
    geojson_update_delay = models.IntegerField(null=True, blank=True)
    shop_option_arr = ArrayField(
        models.CharField(max_length=5000, null=True, blank=True)
    )
    srid = models.CharField(max_length=5000, null=True, blank=True)
    fk_config3d = models.CharField(max_length=5000, null=True, blank=True)

    class Meta:
        managed = settings.TESTING
        db_table = "view_layers_js"
