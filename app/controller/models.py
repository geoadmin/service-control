from django.db import models

from django.utils.translation import gettext_lazy as _


class Provider(models.Model):

    class Meta:
        verbose_name = _("provider")
        verbose_name_plural = _("providers")

    def __str__(self):
        return self.name

    name = models.CharField(_("Provider Name"), max_length=50)
    prefix = models.CharField(_("Provider prefix"), max_length=50)
