from django.db import models
from django.utils.translation import gettext_lazy as _


class Provider(models.Model):

    class Meta:
        verbose_name = _("provider")
        verbose_name_plural = _("providers")

    def __str__(self) -> str:
        return str(self.name_en)

    '''
    Note: The "blank=False" for a model field doesn't prevent DB changes.
          It only has an effect on form validation.
    '''
    name_de = models.CharField(_("Name (German)"))
    name_fr = models.CharField(_("Name (French)"))
    name_en = models.CharField(_("Name (English)"))
    name_it = models.CharField(_("Name (Italian)"), blank=True)
    name_rm = models.CharField(_("Name (Romansh)"), blank=True)

    acronym_de = models.CharField(_("Acronym (German)"))
    acronym_fr = models.CharField(_("Acronym (French)"))
    acronym_en = models.CharField(_("Acronym (English)"))
    acronym_it = models.CharField(_("Acronym (Italian)"), blank=True)
    acronym_rm = models.CharField(_("Acronym (Romansh)"), blank=True)
