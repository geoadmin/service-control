from logging import getLogger

from access.models import User
from cognito.utils.client import Client

logger = getLogger(__name__)


def create_cognito_user(user: User) -> bool:
    """ Add the given user to cognito.

    Returns True, if the user has been created.
    """

    client = Client()
    created = client.create_user(user.username, user.email)
    if created:
        logger.info("User %s created", user.username)
    else:
        logger.critical("User %s already exists, not created", user.username)

    return created


def delete_cognito_user(user: User) -> bool:
    """ Delete the given user from cognito.

    Returns True, if the user has been deleted.
    """

    client = Client()
    deleted = client.delete_user(user.username)
    if deleted:
        logger.info("User %s deleted", user.username)
    else:
        logger.critical("User %s does not exist, not deleted", user.username)
    return deleted


def update_cognito_user(user: User) -> bool:
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
