from ninja import NinjaAPI
import environ
import boto3

api = NinjaAPI()

client = boto3.client("verifiedpermissions")

env = environ.Env()


@api.get('/policy-store')
def get_policy_store(request):
    policy_store_id = env.str('POLICY_STORE_ID')
    return client.get_policy_store(policyStoreId=policy_store_id)


@api.post('/policy')
def create_policy(request):
    policy_store_id = env.str('POLICY_STORE_ID')
    import ipdb
    ipdb.set_trace()
    definition = {
        'static': {
            "description": "My First Policy",
            "statement":
                """
    permit(
  principal in Role::"vacationPhotoJudges",
  action == Action::"view",
  resource == Photo::"vacationPhoto94.jpg"
); """
        }
    }
    return client.create_policy(policyStoreId=policy_store_id, definition=definition)
