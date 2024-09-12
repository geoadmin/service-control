from distributions.models import Attribution, Dataset
from provider.models import Provider

from django.test import TestCase

from unittest import mock
import datetime

class DatasetTestCase(TestCase):

    def test_simple_model_creation(self):
        slug = "ch.bafu.neophyten-haargurke"
        provider = Provider.objects.create(acronym_de="BAFU")
        attribution = Attribution.objects.create(
            name_de="Kantone",
            provider=provider,
        )
        time_created = datetime.datetime(2024, 9, 12, 15, 28, 0, tzinfo=datetime.UTC)
        with mock.patch('django.utils.timezone.now', mock.Mock(return_value=time_created)):
            Dataset.objects.create(
                slug=slug,
                provider=provider,
                attribution=attribution,
            )
        datasets = Dataset.objects.all()

        self.assertEqual(len(datasets), 1)

        dataset = Dataset.objects.last()

        self.assertEqual(dataset.slug, slug)
        self.assertEqual(dataset.provider.acronym_de, "BAFU")
        self.assertEqual(dataset.attribution.name_de, "Kantone")

        self.assertEqual(dataset.created, time_created)
        self.assertEqual(dataset.updated, time_created)


    def test_field_created_matches_creation_time(self):
        provider = Provider.objects.create()
        attribution = Attribution.objects.create(provider=provider)

        time_created = datetime.datetime(2024, 9, 12, 15, 28, 0, tzinfo=datetime.UTC)
        with mock.patch('django.utils.timezone.now', mock.Mock(return_value=time_created)):
            dataset = Dataset.objects.create(
                provider=provider,
                attribution=attribution,
            )
            self.assertEqual(dataset.created, time_created)


    def test_field_updated_matches_update_time(self):
        provider = Provider.objects.create()
        attribution = Attribution.objects.create(provider=provider)
        dataset = Dataset.objects.create(provider=provider, attribution=attribution)

        time_updated = datetime.datetime(2024, 9, 12, 15, 42, 0, tzinfo=datetime.UTC)
        with mock.patch('django.utils.timezone.now', mock.Mock(return_value=time_updated)):
            dataset.slug = "ch.bafu.neophyten-goetterbaum"
            dataset.save()

        self.assertEqual(dataset.updated, time_updated)
