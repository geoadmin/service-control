from django.db import models
from django.utils.translation import pgettext_lazy as _


class Provider(models.Model):

    _context = "Provider model"

    def __str__(self) -> str:
        return str(self.name_en)

    '''
    Note: The "blank=False" for a model field doesn't prevent DB changes.
          It only has an effect on form validation.
    '''
    name_de = models.CharField(_(_context, "Name (German)"))
    name_fr = models.CharField(_(_context, "Name (French)"))
    name_en = models.CharField(_(_context, "Name (English)"))
    name_it = models.CharField(_(_context, "Name (Italian)"), blank=True)
    name_rm = models.CharField(_(_context, "Name (Romansh)"), blank=True)

    acronym_de = models.CharField(_(_context, "Acronym (German)"))
    acronym_fr = models.CharField(_(_context, "Acronym (French)"))
    acronym_en = models.CharField(_(_context, "Acronym (English)"))
    acronym_it = models.CharField(_(_context, "Acronym (Italian)"), blank=True)
    acronym_rm = models.CharField(_(_context, "Acronym (Romansh)"), blank=True)
