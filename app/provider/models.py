from django.db import models
from django.utils.translation import gettext_lazy as _


class Provider(models.Model):

    class Meta:
        verbose_name = _("provider")
        verbose_name_plural = _("providers")

    def __str__(self) -> str:
        return str(self.name_en)

    name_de = models.CharField(_("Name (German)"), blank=True)
    name_fr = models.CharField(_("Name (French)"), blank=True)
    name_it = models.CharField(_("Name (Italian)"), blank=True)
    name_en = models.CharField(_("Name (English)"), blank=True)

    acronym_de = models.CharField(_("Acronym (German)"), blank=True)
    acronym_fr = models.CharField(_("Acronym (French)"), blank=True)
    acronym_it = models.CharField(_("Acronym (Italian)"), blank=True)
    acronym_en = models.CharField(_("Acronym (English)"), blank=True)
