from typing import Any

from distributions.models import Attribution
from provider.models import Provider
from pytest import fixture

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType


@fixture(name='provider')
def fixture_provider(db):
    yield Provider.objects.create(
        slug="ch.bafu",
        acronym_de="BAFU",
        acronym_fr="OFEV",
        acronym_en="FOEN",
        acronym_it="UFAM",
        acronym_rm="UFAM",
        name_de="Bundesamt für Umwelt",
        name_fr="Office fédéral de l'environnement",
        name_en="Federal Office for the Environment",
        name_it="Ufficio federale dell'ambiente",
        name_rm="Uffizi federal per l'ambient",
    )


@fixture(name='attribution')
def fixture_attribution(provider):
    yield Attribution.objects.create(
        slug="ch.bafu.kt",
        name_de="BAFU + Kantone",
        name_fr="OFEV + cantons",
        name_en="FOEN + cantons",
        name_it="UFAM + cantoni",
        name_rm="UFAM + chantuns",
        description_de="Bundesamt für Umwelt und Kantone",
        description_fr="Office fédéral de l'environnement et cantons",
        description_en="Federal Office for the Environment and cantons",
        description_it="Ufficio federale dell'ambiente e cantoni",
        description_rm="Uffizi federal per l'ambient e chantuns",
        provider=provider
    )


@fixture
def django_user_factory(db):
    """A fixture to create Django users, optionally with Django permissions.

    Returns a callable that accepts a username, password, and a list of permissions. Each
    permission should be a tuple containing the application name, model name, and permission name.

    Example usage:

        def test_something(django_user_factory):
            user = django_user_factory('admin', 'password', [('access', 'user', 'add_user')])

    """

    def create_user_with_permissions(
        username: str, password: str, permissions: list[tuple[str, str, str]]
    ) -> Any:
        user = get_user_model().objects.create_user(username=username, password=password)
        for app_label, model, codename in permissions:
            content_type = ContentType.objects.get(app_label=app_label, model=model)
            permission = Permission.objects.get(content_type=content_type, codename=codename)
            user.user_permissions.add(permission)
        return user

    return create_user_with_permissions


@fixture
def cognito_user_response_factory():
    """ A fixture to create Cognito responses containing user data.

    Returns a callable that accepts the following parameters:
    - username: The username of the user.
    - preferred_username: The preferred username of the user.
    - email: The email address of the user.
    - enabled (bool): A flag indicating if the user is enabled.
    - managed (bool): A flag indicating if the user is managed.
    - attributes_key (str): The name of the attributes field, either 'Attributes' for operations
        like list_users and admin_create_user, or 'UserAttributes' for operations like
        admin_get_user.

    Example usage:

        def test_something(cognito_user_response_factory):
            response = cognito_user_response_factory(
                '2ihg2ox304po', 'user', 'user@example.org', enabled=False, managed=True,
                attributes_key='Attributes'
            )
    """

    # pylint: disable=too-many-positional-arguments
    def create_cognito_user_response(
        username,
        preferred_username,
        email='test@example.org',
        enabled=True,
        managed=True,
        attributes_key='Attributes'
    ):

        attributes = [{
            'Name': 'email', 'Value': email
        }, {
            'Name': 'preferred_username', 'Value': preferred_username
        }]
        if managed:
            attributes.append({'Name': settings.COGNITO_MANAGED_FLAG_NAME, 'Value': 'true'})
        return {'Username': username, attributes_key: attributes, 'Enabled': enabled}

    return create_cognito_user_response
