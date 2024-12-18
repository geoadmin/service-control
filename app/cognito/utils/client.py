from typing import TYPE_CHECKING

from boto3 import client

from django.conf import settings

if TYPE_CHECKING:
    from mypy_boto3_cognito_idp.type_defs import AdminGetUserResponseTypeDef
    from mypy_boto3_cognito_idp.type_defs import AttributeTypeTypeDef
    from mypy_boto3_cognito_idp.type_defs import UserTypeTypeDef


def user_attributes_to_dict(attributes: list['AttributeTypeTypeDef']) -> dict[str, str]:
    """ Converts the attributes from a cognito user to a dict. """

    return {attr['Name']: attr['Value'] for attr in attributes}


class Client:
    """ A low level client for managing cognito users.

    Only manages users which have the managed flag defined.
    """

    def __init__(self) -> None:
        self.endpoint_url = settings.COGNITO_ENDPOINT_URL
        self.user_pool_id = settings.COGNITO_POOL_ID
        self.managed_flag_name = settings.COGNITO_MANAGED_FLAG_NAME
        self.client = client("cognito-idp", endpoint_url=self.endpoint_url)

    def list_users(self) -> list['UserTypeTypeDef']:
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
            if user_attributes_to_dict(user['Attributes']).get(self.managed_flag_name) == 'true'
        ]

    def get_user(
        self,
        username: str,
        return_unmanaged: bool = False
    ) -> 'AdminGetUserResponseTypeDef | None':
        """ Get the user with the given cognito username.

        Returns None if the user does not exist or doesn't have the managed flag and
        return_unamanged is False.

        """

        try:
            response = self.client.admin_get_user(UserPoolId=self.user_pool_id, Username=username)
        except self.client.exceptions.UserNotFoundException:
            return None
        if not return_unmanaged:
            attributes = user_attributes_to_dict(response['UserAttributes'])
            if attributes.get(self.managed_flag_name) != 'true':
                return None

        return response

    def create_user(self, username: str, preferred_username: str, email: str) -> bool:
        """ Create a new user.

        Returns False, if a (managed or unmanaged) user already exist.

        Marks the provided email as verified because the newly created user will receive an email
        with a temporary password that they must change upon logging in. If the email is invalid,
        the user will not receive the password and therefore cannot log in, ensuring the email's
        validity.

        """

        user = self.get_user(username, return_unmanaged=True)
        if user is None:
            self.client.admin_create_user(
                UserPoolId=self.user_pool_id,
                Username=username,
                UserAttributes=[{
                    "Name": "email", "Value": email
                }, {
                    "Name": "email_verified", "Value": "true"
                }, {
                    "Name": "preferred_username", "Value": preferred_username
                }, {
                    "Name": self.managed_flag_name, "Value": "true"
                }],
                DesiredDeliveryMediums=['EMAIL']
            )
            return True
        return False

    def delete_user(self, username: str) -> bool:
        """ Delete the user with the given cognito username.

        Returns False, if the user does not exist or doesn't have the managed flag.

        """

        user = self.get_user(username)
        if user is not None:
            self.client.admin_delete_user(UserPoolId=self.user_pool_id, Username=username)
            return True
        return False

    def update_user(self, username: str, preferred_username: str, email: str) -> bool:
        """ Update the user with the given cognito username.

        Only updates changed attributes.

        If the email is changed, it is marked as verified, and the user's password is reset. The
        user must reset the password using the new email before being able to log in. If the email
        is invalid, the user cannot complete the password reset, ensuring the email's validity.

        Returns False, if the user does not exist or doesn't have the managed flag.

        """

        user = self.get_user(username)
        if user is None:
            return False

        old_attributes = user_attributes_to_dict(user['UserAttributes'])
        new_attributes: list[AttributeTypeTypeDef] = []
        reset_password = False
        if old_attributes.get('preferred_username') != preferred_username:
            new_attributes.append({'Name': 'email', 'Value': email})
            new_attributes.append({'Name': 'email_verified', 'Value': 'true'})
            reset_password = True
        if old_attributes.get('email') != email:
            new_attributes.append({'Name': 'preferred_username', 'Value': preferred_username})
        if new_attributes:
            self.client.admin_update_user_attributes(
                UserPoolId=self.user_pool_id, Username=username, UserAttributes=new_attributes
            )

        if reset_password:
            self.client.admin_reset_user_password(UserPoolId=self.user_pool_id, Username=username)

        return True

    def enable_user(self, username: str) -> bool:
        """Enable the user with the given cognito username.

        Returns False, if the user does not exist, or doesn't have the managed flag.
        """

        user = self.get_user(username)
        if user is None:
            return False
        self.client.admin_enable_user(UserPoolId=self.user_pool_id, Username=username)
        return True

    def disable_user(self, username: str) -> bool:
        """Disable the user with the given cognito username.

        Returns False if the user does not exist, or doesn't have the managed flag.
        """

        user = self.get_user(username)
        if user is None:
            return False
        self.client.admin_disable_user(UserPoolId=self.user_pool_id, Username=username)
        return True
