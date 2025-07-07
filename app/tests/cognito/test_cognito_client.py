from unittest.mock import call
from unittest.mock import patch

from cognito.utils.client import Client
from cognito.utils.client import user_attributes_to_dict


def test_user_attributes_to_dict():
    attributes = [{'Name': 'email', 'Value': 'test@example.org'}, {'Name': 'flag', 'Value': 'true'}]
    attributes = user_attributes_to_dict(attributes)
    assert attributes == {'email': 'test@example.org', 'flag': 'true'}


@patch('cognito.utils.client.client')
def test_list_users_returns_only_managed(boto3, cognito_user_response_factory):
    managed = cognito_user_response_factory('2ihg2ox304po', '1234', 'ch.bafu', managed=True)
    unmanaged = cognito_user_response_factory('2ihg2ox304po', '1234', 'ch.bafu', managed=False)
    boto3.return_value.list_users.return_value = {'Users': [managed, unmanaged]}

    client = Client()
    users = client.list_users()
    assert users == [managed]
    assert call().list_users(UserPoolId=client.user_pool_id, Limit=60) in boto3.mock_calls


@patch('cognito.utils.client.client')
def test_list_users_pagination(boto3, cognito_user_response_factory):
    users = [
        cognito_user_response_factory(f'2ihg2ox304po{count}', str(count), True)
        for count in range(1, 131)
    ]
    response_1 = {'Users': users[0:60], 'PaginationToken': '1'}
    response_2 = {'Users': users[60:120], 'PaginationToken': '2'}
    response_3 = {'Users': users[120:130]}
    boto3.return_value.list_users.side_effect = [response_1, response_2, response_3]

    client = Client()
    users = client.list_users()

    assert [user['Username'] for user in users] == [f'2ihg2ox304po{x}' for x in range(1, 131)]
    assert call().list_users(UserPoolId=client.user_pool_id, Limit=60) in boto3.mock_calls
    assert call().list_users(
        UserPoolId=client.user_pool_id, Limit=60, PaginationToken='2'
    ) in boto3.mock_calls
    assert call().list_users(
        UserPoolId=client.user_pool_id, Limit=60, PaginationToken='2'
    ) in boto3.mock_calls


@patch('cognito.utils.client.client')
def test_get_user_returns_managed(boto3, cognito_user_response_factory):
    response = cognito_user_response_factory(
        '2ihg2ox304po', '1234', 'ch.bafu', managed=True, attributes_key='UserAttributes'
    )
    boto3.return_value.admin_get_user.return_value = response

    client = Client()
    user = client.get_user('1234')
    assert user == response
    assert call().admin_get_user(
        UserPoolId=client.user_pool_id, Username='1234'
    ) in boto3.mock_calls


@patch('cognito.utils.client.client')
def test_get_user_does_not_return_unmanaged(boto3, cognito_user_response_factory):
    boto3.return_value.admin_get_user.return_value = cognito_user_response_factory(
        '2ihg2ox304po', '1234', 'ch.bafu', managed=False, attributes_key='UserAttributes'
    )

    client = Client()
    user = client.get_user('1234')
    assert user is None
    assert call().admin_get_user(
        UserPoolId=client.user_pool_id, Username='1234'
    ) in boto3.mock_calls


@patch('cognito.utils.client.client')
def test_get_user_returns_unmanaged(boto3, cognito_user_response_factory):
    response = cognito_user_response_factory(
        '2ihg2ox304po', '1234', 'ch.bafu', managed=False, attributes_key='UserAttributes'
    )
    boto3.return_value.admin_get_user.return_value = response

    client = Client()
    user = client.get_user('1234', return_unmanaged=True)
    assert user == response
    assert call().admin_get_user(
        UserPoolId=client.user_pool_id, Username='1234'
    ) in boto3.mock_calls


@patch('cognito.utils.client.client')
def test_create_user_creates_managed(boto3, cognito_user_response_factory):
    boto3.return_value.admin_get_user.return_value = None

    client = Client()
    created = client.create_user('2ihg2ox304po', '1234', 'test@example.org', 'ch.bafu')
    assert created is True
    assert '().admin_create_user' in [call[0] for call in boto3.mock_calls]
    assert call().admin_create_user(
        UserPoolId=client.user_pool_id,
        Username='2ihg2ox304po',
        UserAttributes=[{
            'Name': 'email', 'Value': 'test@example.org'
        }, {
            'Name': 'email_verified', 'Value': 'true'
        }, {
            'Name': 'preferred_username', 'Value': '1234'
        }, {
            'Name': client.managed_flag_name, 'Value': 'true'
        }, {
            'Name': "custom:providers", 'Value': 'ch.bafu'
        }],
        DesiredDeliveryMediums=['EMAIL']
    ) in boto3.mock_calls


@patch('cognito.utils.client.client')
def test_create_user_does_not_create_if_managed_exists(boto3, cognito_user_response_factory):
    boto3.return_value.admin_get_user.return_value = cognito_user_response_factory(
        '2ihg2ox304po', '1234', 'ch.bafu', managed=True, attributes_key='UserAttributes'
    )

    client = Client()
    created = client.create_user('2ihg2ox304po', '1234', 'test@example.org', 'ch.bafu')
    assert created is False
    assert '().admin_create_user' not in [call[0] for call in boto3.mock_calls]


@patch('cognito.utils.client.client')
def test_create_user_does_not_create_if_unmanaged_exists(boto3, cognito_user_response_factory):
    boto3.return_value.admin_get_user.return_value = cognito_user_response_factory(
        '2ihg2ox304po', '1234', 'ch.bafu', managed=False, attributes_key='UserAttributes'
    )

    client = Client()
    created = client.create_user('2ihg2ox304po', '1234', 'test@example.org', 'ch.bafu')
    assert created is False
    assert '().admin_create_user' not in [call[0] for call in boto3.mock_calls]


@patch('cognito.utils.client.client')
def test_delete_user_deletes_managed(boto3, cognito_user_response_factory):
    boto3.return_value.admin_get_user.return_value = cognito_user_response_factory(
        '2ihg2ox304po', '1234', 'ch.bafu', managed=True, attributes_key='UserAttributes'
    )

    client = Client()
    deleted = client.delete_user('1234')
    assert deleted is True
    assert call().admin_delete_user(
        UserPoolId=client.user_pool_id, Username='1234'
    ) in boto3.mock_calls


@patch('cognito.utils.client.client')
def test_delete_user_does_not_delete_unmanaged(boto3, cognito_user_response_factory):
    boto3.return_value.admin_get_user.return_value = cognito_user_response_factory(
        '2ihg2ox304po', '1234', 'ch.bafu', managed=False, attributes_key='UserAttributes'
    )

    client = Client()
    deleted = client.delete_user('1234')
    assert deleted is False
    assert call().admin_delete_user(
        UserPoolId=client.user_pool_id, Username='1234'
    ) not in boto3.mock_calls


@patch('cognito.utils.client.client')
def test_update_user_updates_managed(boto3, cognito_user_response_factory):
    boto3.return_value.admin_get_user.return_value = cognito_user_response_factory(
        '2ihg2ox304po', '1234', 'ch.bafu', managed=True, attributes_key='UserAttributes'
    )

    client = Client()
    updated = client.update_user('2ihg2ox304po', '5678', 'new@example.org', 'ch.bafu')
    assert updated is True
    assert '().admin_update_user_attributes' in [call[0] for call in boto3.mock_calls]
    assert '().admin_reset_user_password' in [call[0] for call in boto3.mock_calls]
    assert call().admin_update_user_attributes(
        UserPoolId=client.user_pool_id,
        Username='2ihg2ox304po',
        UserAttributes=[{
            'Name': 'email', 'Value': 'new@example.org'
        }, {
            'Name': 'email_verified', 'Value': 'true'
        }, {
            'Name': 'preferred_username', 'Value': '5678'
        }]
    ) in boto3.mock_calls
    assert call().admin_reset_user_password(
        UserPoolId=client.user_pool_id, Username='2ihg2ox304po'
    ) in boto3.mock_calls


@patch('cognito.utils.client.client')
def test_update_user_updates_partial_managed(boto3, cognito_user_response_factory):
    boto3.return_value.admin_get_user.return_value = cognito_user_response_factory(
        '2ihg2ox304po', '1234', 'ch.bafu', managed=True, attributes_key='UserAttributes'
    )

    client = Client()
    updated = client.update_user('2ihg2ox304po', '5678', 'test@example.org', 'ch.bafu')
    assert updated is True
    assert '().admin_update_user_attributes' in [call[0] for call in boto3.mock_calls]
    assert '().admin_reset_user_password' not in [call[0] for call in boto3.mock_calls]
    assert call().admin_update_user_attributes(
        UserPoolId=client.user_pool_id,
        Username='2ihg2ox304po',
        UserAttributes=[{
            'Name': 'preferred_username', 'Value': '5678'
        }]
    ) in boto3.mock_calls


@patch('cognito.utils.client.client')
def test_update_user_does_not_update_unchanged_managed(boto3, cognito_user_response_factory):
    boto3.return_value.admin_get_user.return_value = cognito_user_response_factory(
        '2ihg2ox304po', '1234', 'ch.bafu', managed=True, attributes_key='UserAttributes'
    )

    client = Client()
    updated = client.update_user('2ihg2ox304po', '1234', 'test@example.org', 'ch.bafu')
    assert updated is True
    assert '().admin_update_user_attributes' not in [call[0] for call in boto3.mock_calls]
    assert '().admin_reset_user_password' not in [call[0] for call in boto3.mock_calls]


@patch('cognito.utils.client.client')
def test_update_user_does_not_update_unmanaged(boto3, cognito_user_response_factory):
    boto3.return_value.admin_get_user.return_value = cognito_user_response_factory(
        '2ihg2ox304po', '1234', 'ch.bafu', managed=False, attributes_key='UserAttributes'
    )

    client = Client()
    updated = client.update_user('2ihg2ox304po', '1234', 'test@example.org', 'ch.bafu')
    assert updated is False
    assert '().admin_update_user_attributes' not in [call[0] for call in boto3.mock_calls]


@patch('cognito.utils.client.client')
def test_disable_user_disables_managed(boto3, cognito_user_response_factory):
    boto3.return_value.admin_get_user.return_value = cognito_user_response_factory(
        '2ihg2ox304po', '1234', 'ch.bafu', managed=True, attributes_key='UserAttributes'
    )

    client = Client()
    disabled = client.disable_user('1234')
    assert disabled is True
    assert call().admin_disable_user(
        UserPoolId=client.user_pool_id, Username='1234'
    ) in boto3.mock_calls


@patch('cognito.utils.client.client')
def test_disable_user_does_not_disable_unmanaged(boto3, cognito_user_response_factory):
    boto3.return_value.admin_get_user.return_value = cognito_user_response_factory(
        '2ihg2ox304po', '1234', 'ch.bafu', managed=False, attributes_key='UserAttributes'
    )

    client = Client()
    disabled = client.disable_user('1234')
    assert disabled is False
    assert call().admin_disable_user(
        UserPoolId=client.user_pool_id, Username='1234'
    ) not in boto3.mock_calls


@patch('cognito.utils.client.client')
def test_enable_user_enables_managed(boto3, cognito_user_response_factory):
    boto3.return_value.admin_get_user.return_value = cognito_user_response_factory(
        '2ihg2ox304po', '1234', 'ch.bafu', managed=True, attributes_key='UserAttributes'
    )

    client = Client()
    enabled = client.enable_user('1234')
    assert enabled is True
    assert call().admin_enable_user(
        UserPoolId=client.user_pool_id, Username='1234'
    ) in boto3.mock_calls


@patch('cognito.utils.client.client')
def test_enable_user_does_not_enable_unmanaged(boto3, cognito_user_response_factory):
    boto3.return_value.admin_get_user.return_value = cognito_user_response_factory(
        '2ihg2ox304po', '1234', 'ch.bafu', managed=False, attributes_key='UserAttributes'
    )

    client = Client()
    enabled = client.enable_user('1234')
    assert enabled is False
    assert call().admin_enable_user(
        UserPoolId=client.user_pool_id, Username='1234'
    ) not in boto3.mock_calls
