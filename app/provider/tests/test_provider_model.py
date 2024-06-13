from faker import Faker
from provider.models import Provider

from django.test import TestCase

fake = Faker()


class ProviderTestCase(TestCase):

    def test_simple_model_creation(self):
        name = fake.company()
        prefix = fake.company_suffix()
        Provider.objects.create(name=name, prefix=prefix)

        providers = Provider.objects.all()

        self.assertEqual(len(providers), 1)

        provider = Provider.objects.last()
        self.assertEqual(provider.name, name)
        self.assertEqual(provider.prefix, prefix)
