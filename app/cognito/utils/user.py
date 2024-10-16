from logging import getLogger

from cognito.utils.client import Client

logger = getLogger(__name__)


# TODO: Replace me with the actual user model
class User:
    username: str
    email: str
    is_active: bool


def create_user(user: User) -> bool:
    """ Add the given user to cognito.

    Returns True, if the user has been created.
    """

    client = Client()
    created = client.create_user(user.username, user.email)
    if created:
        logger.info("User %s created", user.username)
    else:
        logger.warning("User %s already exists, not created", user.username)

    return created


def disable_user(user: User) -> bool:
    """ Disable the given user in cognito.

    Returns True, if the user has been disabled.
    """

    client = Client()
    disabled = client.disable_user(user.username)
    if disabled:
        logger.info("User %s disabled", user.username)
    else:
        logger.warning("User %s does not exist, not disabled", user.username)
    return disabled


def update_user(user: User) -> bool:
    """ Update the given user in cognito.

    Returns True, if the user has been updated.
    """

    client = Client()
    updated = client.update_user(user.username, user.email)
    if updated:
        logger.info("User %s updated", user.username)
    else:
        logger.warning("User %s does not exist, not updated", user.username)
    return updated
