from logging import getLogger

from cognito.utils.client import Client

logger = getLogger(__name__)


# TODO: Replace me with the actual user model
class User:
    id: int
    email: str


def add_user(user: User) -> None:
    """ Add the given user to cognito.

    Update the user, if he already exists.
    """

    client = Client()
    username = str(user.id)
    existing = client.get_user(username)
    if existing is not None:
        logger.warning("User %s already exists, updating", username)
        client.update_user(username, user.email)
    else:
        client.create_user(username, user.email)
    logger.info("User %s created", username)


def delete_user(user: User) -> None:
    """ Delete the given user from cognito. """

    client = Client()
    username = str(user.id)
    existing = client.get_user(username)
    if existing is not None:
        client.delete_user(username)
    else:
        logger.warning("User %s does not exist, ignoring", username)
    logger.info("User %s deleted", username)


def update_user(user: User) -> None:
    """ Update the given user in cognito.

    Add the user, if he not already exists.
    """

    client = Client()
    username = str(user.id)
    existing = client.get_user(username)
    if existing is not None:
        client.update_user(username, user.email)
    else:
        logger.warning("User %s does not exist, adding", username)
        client.create_user(username, user.email)
    logger.info("User %s updated", username)
