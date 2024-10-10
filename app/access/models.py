from django.db import models
from django.utils.translation import pgettext_lazy as _


class User(models.Model):

    _context = "User model"

    def __str__(self) -> str:
        return str(self.first_name) + str(self.last_name)

    first_name = models.CharField(_(_context, "First name"))
    last_name = models.CharField(_(_context, "Last name"))
    email = models.EmailField(_(_context, "Email"))

    provider = models.ForeignKey("provider.Provider", on_delete=models.CASCADE)
