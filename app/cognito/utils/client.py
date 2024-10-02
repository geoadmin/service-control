from boto3 import client
from mypy_boto3_cognito_idp.type_defs import AdminGetUserResponseTypeDef
from mypy_boto3_cognito_idp.type_defs import UserTypeTypeDef

from django.conf import settings


class Client:
    """ A low level client for managing cognito users. """

    def __init__(self) -> None:
        self.endpoint_url = settings.COGNITO_ENDPOINT_URL
        self.user_pool_id = settings.COGNITO_POOL_ID
        self.client = client("cognito-idp", endpoint_url=self.endpoint_url)

    def get_users(self) -> list[UserTypeTypeDef]:
        response = self.client.list_users(UserPoolId=self.user_pool_id)
        return response['Users']

    def get_user(self, username: str) -> AdminGetUserResponseTypeDef | None:
        try:
            response = self.client.admin_get_user(UserPoolId=self.user_pool_id, Username=username)
        except self.client.exceptions.UserNotFoundException:
            return None

        return response

    def create_user(self, username: str, email: str) -> UserTypeTypeDef:
        response = self.client.admin_create_user(
            UserPoolId=self.user_pool_id,
            Username=username,
            UserAttributes=[
                {
                    "Name": "email", "Value": email
                },
            ],
            DesiredDeliveryMediums=['EMAIL']
        )
        return response['User']

    def delete_user(self, username: str) -> None:
        self.client.admin_delete_user(UserPoolId=self.user_pool_id, Username=username)

    def update_user(self, username: str, email: str) -> None:
        self.client.admin_update_user_attributes(
            UserPoolId=self.user_pool_id,
            Username=username,
            UserAttributes=[
                {
                    "Name": "email", "Value": email
                },
            ],
        )
