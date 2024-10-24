from django.db import models
from django.utils.translation import pgettext_lazy as _


class Attribution(models.Model):

    _context = "Attribution Model"

    def __str__(self) -> str:
        return str(self.name_en)

    name_de = models.CharField(_(_context, "Name (German)"))
    name_fr = models.CharField(_(_context, "Name (French)"))
    name_en = models.CharField(_(_context, "Name (English)"))
    name_it = models.CharField(_(_context, "Name (Italian)"), null=True, blank=True)
    name_rm = models.CharField(_(_context, "Name (Romansh)"), null=True, blank=True)

    description_de = models.CharField(_(_context, "Description (German)"))
    description_fr = models.CharField(_(_context, "Description (French)"))
    description_en = models.CharField(_(_context, "Description (English)"))
    description_it = models.CharField(_(_context, "Description (Italian)"), null=True, blank=True)
    description_rm = models.CharField(_(_context, "Description (Romansh)"), null=True, blank=True)

    provider = models.ForeignKey("provider.Provider", on_delete=models.CASCADE)

    _legacy_id = models.IntegerField(
        _(_context, "Legacy ID"),
        null=True,
        blank=True,
        db_index=False,
        help_text="This field is used to track objects imported from the BOD"
    )


class Dataset(models.Model):

    _context = "Dataset Model"

    def __str__(self) -> str:
        return str(self.slug)


    slug = models.SlugField(_(_context, "Slug"), max_length=100)
    created = models.DateTimeField(_(_context, "Created"), auto_now_add=True)
    updated = models.DateTimeField(_(_context, "Updated"), auto_now=True)

    provider = models.ForeignKey("provider.Provider", on_delete=models.CASCADE)
    attribution = models.ForeignKey(Attribution, on_delete=models.CASCADE)

    _legacy_id = models.IntegerField(
        _(_context, "Legacy ID"),
        null=True,
        blank=True,
        db_index=False,
        help_text="This field is used to track objects imported from the BOD"
    )
