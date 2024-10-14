from logging import getLogger

from cognito.utils.client import Client

logger = getLogger(__name__)


# TODO: Replace me with the actual user model
class User:
    username: str
    email: str


def add_user(user: User) -> None:
    """ Add the given user to cognito.

    Update the user, if he already exists.
    """

    client = Client()
    username = str(user.username)
    existing = client.get_user(username)
    if existing is not None:
        client.update_user(username, user.email)
        logger.warning("User %s already exists, updated instead of created", username)
    else:
        client.create_user(username, user.email)
        logger.info("User %s created", username)


def delete_user(user: User) -> None:
    """ Delete the given user from cognito. """

    client = Client()
    username = str(user.username)
    existing = client.get_user(username)
    if existing is not None:
        client.delete_user(username)
        logger.info("User %s deleted", username)
    else:
        logger.warning("User %s does not exist, not deleted", username)


def update_user(user: User) -> None:
    """ Update the given user in cognito.

    Add the user, if he not already exists.
    """

    client = Client()
    username = str(user.username)
    existing = client.get_user(username)
    if existing is not None:
        client.update_user(username, user.email)
        logger.info("User %s updated", username)
    else:
        client.create_user(username, user.email)
        logger.warning("User %s does not exist, creating", username)
