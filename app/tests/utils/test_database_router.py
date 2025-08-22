from bod.models import BodContactOrganisation
from provider.models import Provider
from pytest import raises


def test_database_routing_inside_tests():
    assert BodContactOrganisation.objects.db == "default"
    assert Provider.objects.db == "default"


def test_database_routing_outside_tests(settings):
    settings.TESTING = False
    assert BodContactOrganisation.objects.db == "bod"
    assert Provider.objects.db == "default"


def test_writing_to_bod_supported_inside_tests(db):
    BodContactOrganisation.objects.create()
    assert BodContactOrganisation.objects.count() == 1


def test_writing_to_bod_not_supported_outside_tests(settings, db):
    settings.TESTING = False
    with raises(RuntimeError):
        BodContactOrganisation.objects.create()
