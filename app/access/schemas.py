from ninja import Schema


class UserSchema(Schema):

    username: str
    first_name: str
    last_name: str
    email: str
    provider_id: str


class UserListSchema(Schema):
    items: list[UserSchema]


class AccessDatasetSchema(Schema):
    id: str
    # title: str
    provider_id: str
    action: list[str]


class AccessDatasetListSchema(Schema):
    username: str
    roles: list[str]
    items: list[AccessDatasetSchema]
