from typing import TYPE_CHECKING
from typing import Any
from typing import TextIO

import environ
from access.models import Action
from access.models import ResourceType
from access.models import RoleAccess
from utils.command import CustomBaseCommand
from verifiedpermissions.utils.client import VPClient

from django.core.management.base import CommandParser

if TYPE_CHECKING:
    from mypy_boto3_verifiedpermissions.type_defs import StaticPolicyDefinitionTypeDef

env = environ.Env()


class Command(CustomBaseCommand):
    help = "Synchronizes local users with cognito"

    def __init__(
        self,
        stdout: TextIO | None = None,
        stderr: TextIO | None = None,
        no_color: bool = False,
        force_color: bool = False
    ):
        super().__init__(stdout, stderr, no_color, force_color)
        self.client = VPClient()
        self.namespace = env.str('VERIFIED_PERMISSIONS_NAMESPACE', default='poc')
        self.user_pool_id = env.str('COGNITO_POOL_ID', default='local_PoolPrty')
        self.counts = {
            'resources created': 0,
            'actions created': 0,
            'policies deleted': 0,
            'policies created': 0
        }

    def add_arguments(self, parser: CommandParser) -> None:
        super().add_arguments(parser)
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Dry run, abort transaction in the end',
        )

    def sync_schema(self) -> None:
        """ Synchronizes verified permissions schema """

        schema = {}
        schema[self.namespace] = BASE_SCHEMA
        resource_types = ResourceType.objects.all()
        for rt in resource_types:
            schema = self.client.schema_add_resource_type(schema, rt.resource_type_id)

        actions = Action.objects.all()
        for a in actions:
            schema = self.client.schema_add_action(schema, a.action_id)

        self.counts['resources created'] = len(resource_types)
        self.counts['actions created'] = len(actions)
        if not self.options['dry_run']:
            self.client.put_schema(schema)

    def sync_policies(self) -> None:
        """ Synchronizes verified permissions policies """
        policies = self.client.all_policies()
        for p in policies:
            self.counts['policies deleted'] += 1
            self.print(f"deleting policy {p['policyId']}")
            if not self.options['dry_run']:
                self.client.delete_policy(p['policyId'])

        role_access = RoleAccess.objects.all()
        for ra in role_access:
            self.counts['policies created'] += 1
            self.print(f'creating policy for role access {ra.role} {ra.resource_type}')
            if not self.options['dry_run']:
                policy_id = self.client.create_policy(
                    str(ra.role), ra.actions, str(ra.resource_type)
                )
                ra.policy_id = policy_id
                ra.save()

        for base_p in BASE_POLICIES:
            self.counts['policies created'] += 1
            base_p['statement'] = base_p['statement'].format(
                namespace=self.namespace, user_pool=self.user_pool_id
            )
            self.print(f"creating base policy {base_p['description']}")
            if not self.options['dry_run']:
                policy_id = self.client.create_static_policy(base_p)

    def handle(self, *args: Any, **options: Any) -> None:
        """ Main entry point of command. """
        self.sync_schema()
        self.sync_policies()

        # Print counts
        printed = False
        for operation, count in self.counts.items():
            if count:
                printed = True
                self.print_success(f'{count} {operation}')
        if not printed:
            self.print_success('nothing to be done')

        if self.options['dry_run']:
            self.print_warning('dry run, nothing has been done')


BASE_POLICIES: list['StaticPolicyDefinitionTypeDef'] = [{
    'description': 'PPGDI Admin',
    'statement':
        """permit (
    principal in {namespace}::UserGroup::\"{user_pool}|ppbgdi-admin\",
    action,
    resource
);"""
}]

BASE_SCHEMA = {
    "entityTypes": {
        "User": {
            "memberOfTypes": ["UserGroup"],
            "shape": {
                "type": "Record",
                "attributes": {
                    "preferred_username": {
                        "type": "String", "required": False
                    },
                    "sub": {
                        "type": "String", "required": True
                    },
                    "dev:custom:managed_by_service": {
                        "type": "Boolean", "required": False
                    },
                    "email": {
                        "type": "String", "required": False
                    },
                    "name": {
                        "type": "String", "required": False
                    },
                }
            }
        },
        "UserGroup": {
            "memberOfTypes": [], "shape": {
                "type": "Record", "attributes": {}
            }
        }
    },
    "actions": {},
    "commonTypes": {
        "ReusedContext": {
            "type": "Record",
            "attributes": {
                "token": {
                    "type": "Record",
                    "attributes": {
                        "providers": {
                            "required": True, "type": "Set", "element": {
                                "type": "String"
                            }
                        }
                    }
                }
            }
        },
        "ProviderResource": {
            "type": "Record", "attributes": {
                "provider": {
                    "required": True, "type": "String"
                }
            }
        }
    }
}
