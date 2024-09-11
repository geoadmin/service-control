from django.db import models

from django.utils.translation import gettext_lazy as _


class Attribution(models.Model):

    class Meta:
        verbose_name = _("attribution")
        verbose_name_plural = _("attributions")

    def __str__(self) -> str:
        return str(self.name_en)

    name_de = models.CharField(_("Name (German)"))
    name_fr = models.CharField(_("Name (French)"))
    name_en = models.CharField(_("Name (English)"))
    name_it = models.CharField(_("Name (Italian)"), blank=True)
    name_rm = models.CharField(_("Name (Romansh)"), blank=True)

    description_de = models.CharField(_("Description (German)"))
    description_fr = models.CharField(_("Description (French)"))
    description_en = models.CharField(_("Description (English)"))
    description_it = models.CharField(_("Description (Italian)"), blank=True)
    description_rm = models.CharField(_("Description (Romansh)"), blank=True)

    provider = models.ForeignKey("provider.Provider", on_delete=models.CASCADE)
