from boto3 import client
from mypy_boto3_cognito_idp.type_defs import AdminGetUserResponseTypeDef
from mypy_boto3_cognito_idp.type_defs import AttributeTypeTypeDef
from mypy_boto3_cognito_idp.type_defs import UserTypeTypeDef

from django.conf import settings


def user_attributes_to_dict(attributes: list[AttributeTypeTypeDef]) -> dict[str, str]:
    """ Converts the attributes from a cognito user to a dict. """

    return {attr['Name']: attr['Value'] for attr in attributes}


class Client:
    """ A low level client for managing cognito users.

    Only manages users which have managed flag defined.
    """

    def __init__(self) -> None:
        self.endpoint_url = settings.COGNITO_ENDPOINT_URL
        self.user_pool_id = settings.COGNITO_POOL_ID
        self.client = client("cognito-idp", endpoint_url=self.endpoint_url)

    def list_users(self) -> list[UserTypeTypeDef]:
        """ Get a list of managed users. """

        response = self.client.list_users(UserPoolId=self.user_pool_id, Limit=60)
        users = response['Users']

        while response.get('PaginationToken'):
            response = self.client.list_users(
                UserPoolId=self.user_pool_id, Limit=60, PaginationToken=response['PaginationToken']
            )
            users.extend(response['Users'])

        return [
            user for user in users
            if user_attributes_to_dict(user['Attributes']).get('custom:managed') == 'True'
        ]

    def get_user(
        self, username: str, return_unmanaged: bool = False
    ) -> AdminGetUserResponseTypeDef | None:
        """ Get the user with the given username.

        Returns None if the user does not exist or doesn't have the managed flag and
        return_unamanged is False.

        """

        try:
            response = self.client.admin_get_user(UserPoolId=self.user_pool_id, Username=username)
        except self.client.exceptions.UserNotFoundException:
            return None
        if not return_unmanaged:
            attributes = user_attributes_to_dict(response['UserAttributes'])
            if attributes.get('custom:managed') != 'True':
                return None

        return response

    def create_user(self, username: str, email: str) -> bool:
        """ Create a new user.

        Returns False, if a (managed or unmanaged) user already exist.

        """

        user = self.get_user(username, return_unmanaged=True)
        if user is None:
            self.client.admin_create_user(
                UserPoolId=self.user_pool_id,
                Username=username,
                UserAttributes=[{
                    "Name": "email", "Value": email
                }, {
                    "Name": "custom:managed", "Value": "True"
                }],
                DesiredDeliveryMediums=['EMAIL']
            )
            return True
        return False

    def delete_user(self, username: str) -> bool:
        """ Delete the given user.

        Returns False, if the user does not exist or doesn't have the managed flag.

        """

        user = self.get_user(username)
        if user is not None:
            self.client.admin_delete_user(UserPoolId=self.user_pool_id, Username=username)
            return True
        return False

    def update_user(self, username: str, email: str) -> bool:
        """ Update the given user.

        Returns False, if the user does not exist or doesn't have the managed flag.

        """

        user = self.get_user(username)
        if user is not None:
            self.client.admin_update_user_attributes(
                UserPoolId=self.user_pool_id,
                Username=username,
                UserAttributes=[{
                    "Name": "email", "Value": email
                }, {
                    "Name": "custom:managed", "Value": "True"
                }]
            )
            return True
        return False
