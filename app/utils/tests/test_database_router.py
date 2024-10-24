from bod.models import BodContactOrganisation
from provider.models import Provider

from django.test import TestCase


class DatabaseRouterTestCase(TestCase):

    def test_database_routing_inside_tests(self):
        self.assertEqual(BodContactOrganisation.objects.db, 'default')
        self.assertEqual(Provider.objects.db, 'default')

    def test_database_routing_outside_tests(self):
        with self.settings(TESTING=False):
            self.assertEqual(BodContactOrganisation.objects.db, 'bod')
            self.assertEqual(Provider.objects.db, 'default')

    def test_writing_to_bod_supported_inside_tests(self):
        BodContactOrganisation.objects.create()
        self.assertEqual(BodContactOrganisation.objects.count(), 1)

    def test_writing_to_bod_not_supported_outside_tests(self):
        with self.settings(TESTING=False):
            self.assertRaises(RuntimeError, BodContactOrganisation.objects.create)
