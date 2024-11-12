from datetime import datetime

from django.db import models
from django.utils.translation import pgettext_lazy as _


class SoftDeleteModel(models.Model):
    """SoftDeleteModel does not remove records from the database, but sets the current timestamp.
    Records that have the 'deleted_at' timestamp set are considered deleted.

    Advantage is that records can be reactivated if needed. Downside is that any foreign keys are
    still active, so related records can not be (hard) deleted.
    """
    _context = "Generic model"

    deleted_at = models.DateTimeField(_(_context, "deleted at"), null=True, blank=True)

    class Meta:
        abstract = True

    def delete(self, using=None, keep_parents=False):
        self.deleted_at = datetime.now()
        self.save()


class SoftDeleteModelManager(models.Manager):
    """SoftDeleteModelManager excludes results that are soft deleted.

    """

    def get_queryset(self) -> models.QuerySet:
        return super().get_queryset().filter(deleted_at__isnull=True)
