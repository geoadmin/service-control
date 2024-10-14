import pytest
from access.schemas import UserSchema
from pydantic import ValidationError


def test_userschema_created_for_valid_email():
    actual = UserSchema(
        username="dude",
        first_name="Jeffrey",
        last_name="Lebowski",
        email="dude@bowling.com",
        provider_id=2,
    )
    assert actual.username == "dude"
    assert actual.first_name == "Jeffrey"
    assert actual.last_name == "Lebowski"
    assert actual.email == "dude@bowling.com"
    assert actual.provider_id == 2


def test_userschema_raises_exception_for_invalid_email():
    with pytest.raises(ValidationError):
        UserSchema(
            username="dude",
            first_name="Jeffrey",
            last_name="Lebowski",
            email="dude_at_bowling_dot_com",
            provider_id=2,
        )
