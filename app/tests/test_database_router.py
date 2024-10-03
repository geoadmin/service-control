import warnings
from copy import deepcopy

from bod.models import BodContactOrganisation
from provider.models import Provider

from django.conf import settings
from django.test import TestCase


class DatabaseRouterTestCase(TestCase):

    databases = {'default', 'bod'}

    def test_database_routing(self):
        self.assertEqual(BodContactOrganisation.objects.db, 'bod')
        self.assertEqual(Provider.objects.db, 'default')

    def test_writing_to_bod_supported_within_tests(self):
        BodContactOrganisation.objects.create()
        self.assertEqual(BodContactOrganisation.objects.count(), 1)

    def test_writing_to_bod_not_supported_outside_tests(self):
        with warnings.catch_warnings():
            # we know that manipulating settings.DATABASES is a bad idea, ignore this warning
            warnings.simplefilter("ignore", UserWarning)
            databases = deepcopy(settings.DATABASES)
            databases['bod']['NAME'] = '__bod_db___'
            with self.settings(DATABASES=databases):
                self.assertRaises(RuntimeError, BodContactOrganisation.objects.create)
