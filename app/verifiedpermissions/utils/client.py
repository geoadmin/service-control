import json
from typing import TYPE_CHECKING
from typing import Any

from boto3 import client

from django.conf import settings

# from access.models import ResourceType

if TYPE_CHECKING:
    from mypy_boto3_verifiedpermissions.type_defs import PolicyItemTypeDef
    from mypy_boto3_verifiedpermissions.type_defs import StaticPolicyDefinitionTypeDef


class VPClient:
    """ A low level client for managing verified permissions.
    """

    def __init__(self) -> None:
        self.policy_store_id = settings.VERIFIED_PERMISSIONS_STORE_ID  # settings.COGNITO_POOL_ID
        self.namespace = settings.VERIFIED_PERMISSIONS_NAMESPACE
        self.user_pool_id = settings.COGNITO_POOL_ID
        self.group_resource_suffix = "_grp"

        self.client = client('verifiedpermissions')

        # To connect from local (with aws sso)
        # from boto3 import Session
        # session = Session(profile_name='swisstopo-bgdi-dev', region_name='eu-central-1')
        # self.client = session.client("verifiedpermissions")

    def parent_resource(self, r: str) -> str:
        """Always create a parent resource for all resources. Once cedar v4 is available in AWS
        this will no longer be needed as permissions can check the resource type with key word 'is'.
        """

        return r + self.group_resource_suffix

    def get_schema(self) -> str:
        response = self.client.get_schema(policyStoreId=self.policy_store_id)
        return str(response['schema'])

    def put_schema(self, schema: dict[str, Any]) -> None:
        self.client.put_schema(
            policyStoreId=self.policy_store_id, definition={'cedarJson': json.dumps(schema)}
        )

    def add_update_resource_type_to_schema(self, resource_type_name: str) -> None:
        schema_string = self.get_schema()
        schema = json.loads(schema_string)
        schema = self.schema_add_resource_type(schema, resource_type_name)
        self.put_schema(schema)

    def remove_resource_type_from_schema(self, resource_type_name: str) -> None:
        schema_string = self.get_schema()
        schema = json.loads(schema_string)
        del schema[self.namespace]["entityTypes"][self.parent_resource(resource_type_name)]
        del schema[self.namespace]["entityTypes"][resource_type_name]

        for v in schema[self.namespace]["actions"].values():
            if resource_type_name in v["appliesTo"]["resourceTypes"]:
                v["appliesTo"]["resourceTypes"].remove(resource_type_name)

        self.client.put_schema(
            policyStoreId=self.policy_store_id, definition={'cedarJson': json.dumps(schema)}
        )

    def add_action_to_schema(self, action_name: str) -> None:
        schema_string = self.get_schema()
        schema = json.loads(schema_string)
        schema = self.schema_add_action(schema, action_name)
        self.client.put_schema(
            policyStoreId=self.policy_store_id, definition={'cedarJson': json.dumps(schema)}
        )

    def remove_action_from_schema(self, action_name: str) -> None:
        schema_string = self.get_schema()
        schema = json.loads(schema_string)

        if action_name in schema[self.namespace]["actions"]:
            del schema[self.namespace]["actions"][action_name]

        self.client.put_schema(
            policyStoreId=self.policy_store_id, definition={'cedarJson': json.dumps(schema)}
        )

    def all_policies(self) -> list['PolicyItemTypeDef']:
        policies = []
        resp = self.client.list_policies(
            policyStoreId=self.policy_store_id,
            maxResults=50,  # limit is 50
        )
        policies.extend(resp['policies'])
        next_token = resp.get('nextToken', None)
        while next_token is not None:
            resp = self.client.list_policies(
                policyStoreId=self.policy_store_id,
                nextToken=next_token,
                maxResults=50,  # limit is 50
            )
            next_token = resp.get('nextToken', None)
            policies.extend(resp['policies'])
        return policies

    def create_policy(self, role: str, actions: list[str], resource_type: str) -> str:
        policy = f"""permit (
            principal in {self.namespace}::UserGroup::"{self.user_pool_id}|{role}",
            action in
                [{",".join([f"{self.namespace}::Action::\"{action}\"" for action in actions])}],
            resource in {self.namespace}::{resource_type}_grp::"All"
        )
        when {{ context.token["providers"].contains(resource.provider) }};"""

        return self.create_static_policy({
            'description': f'{role} {resource_type}', 'statement': policy
        })

    def create_static_policy(self, policy: 'StaticPolicyDefinitionTypeDef') -> str:
        response = self.client.create_policy(
            # clientToken='string', # Set for idempotency on retries
            policyStoreId=self.policy_store_id,
            definition={
                'static': policy,
            }
        )
        return str(response['policyId'])

    def delete_policy(self, policy_id: str) -> None:
        self.client.delete_policy(policyStoreId=self.policy_store_id, policyId=policy_id)

    def schema_add_resource_type(self, schema: dict[str, Any],
                                 resource_type_name: str) -> dict[str, Any]:
        schema[self.namespace]["entityTypes"][self.parent_resource(resource_type_name)] = {
            "memberOfTypes": [], "shape": {
                "type": "Record", "attributes": {}
            }
        }
        schema[self.namespace]["entityTypes"][resource_type_name] = {
            "memberOfTypes": [self.parent_resource(resource_type_name)],
            "shape": {
                "type": "ProviderResource"
            }
        }
        for v in schema[self.namespace]["actions"].values():
            v["appliesTo"]["resourceTypes"].append(resource_type_name)
        return schema

    def schema_add_action(self, schema: dict[str, Any], action: str) -> dict[str, Any]:
        resource_types = []
        for entity_type, v in schema[self.namespace]["entityTypes"].items():
            if v["shape"]["type"] == "ProviderResource":
                resource_types.append(entity_type)

        schema[self.namespace]["actions"][action] = {
            "memberOf": [],
            "appliesTo": {
                "context": {
                    "type": "ReusedContext"
                },
                "principalTypes": ["User"],
                "resourceTypes": resource_types
            }
        }
        return schema
