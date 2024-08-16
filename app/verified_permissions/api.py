from ninja import NinjaAPI, Schema
import environ
import boto3

api = NinjaAPI()

client = boto3.client("verifiedpermissions")

env = environ.Env()


@api.get('/policy-store')
def get_policy_store(request):
    policy_store_id = env.str('POLICY_STORE_ID')
    return client.get_policy_store(policyStoreId=policy_store_id)


SCHEMA = """
{
    "ServiceStac": {
        "entityTypes": {
            "UserGroup": {
                "shape": {
                    "type": "Record",
                    "attributes": {}
                }
            },
            "Application": {
                "shape": {
                    "type": "Record",
                    "attributes": {}
                }
            },
            "User": {
                "memberOfTypes": [
                    "UserGroup"
                ],
                "shape": {
                    "type": "Record",
                    "attributes": {}
                }
            }
        },
        "actions": {
            "get /collections/ch.bafu.irgend": {
                "appliesTo": {
                    "principalTypes": [
                        "User"
                    ],
                    "resourceTypes": [
                        "Application"
                    ],
                    "context": {
                        "attributes": {},
                        "type": "Record"
                    }
                }
            }
        }
    }
}
"""


# I think we need to be able to update the schema since it contains the
# resources. the resources are subject to change when new collections are added?!
@api.post('/policy-store/schema')
def update_policy_store_schema(request):
    policy_store_id = env.str('POLICY_STORE_ID')
    return client.put_schema(policyStoreId=policy_store_id, definition={'cedarJson': SCHEMA})


@api.post('/policy')
def create_policy(request):
    policy_store_id = env.str('POLICY_STORE_ID')
    cognito_pool_id = env.str('COGNITO_POOL_ID')
    user_id = ""
    definition = {
        # TODO user_pool_id
        'static': {
            "description": "My First POC Policy",
            "statement":
                f"""
                permit(
                    principal == ServiceStac::User::"{cognito_pool_id}|{user_id}",
                    action == ServiceStac::Action::"get /collections",
                    resource
                ); """
        }
    }
    try:
        result = client.create_policy(policyStoreId=policy_store_id, definition=definition)
        return result
    except Exception as e:
        print(e)


class User(Schema):
    email: str
    username: str


@api.post('/user')
def create_user(request, user: User):
    cognito_pool_id = env.str('COGNITO_POOL_ID')
    cognito_user_pool_name = env.str('COGNITO_USER_POOL_NAME')

    cognito_client = boto3.client("cognito-idp")

    cognito_client.admin_create_user(
        UserPoolId=cognito_pool_id,
        Username=user.username,
        UserAttributes=[{
            'Name': 'email', 'Value': user.email
        }]
    )
