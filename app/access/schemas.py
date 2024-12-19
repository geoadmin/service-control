from ninja import Schema


class UserSchema(Schema):

    username: str
    first_name: str
    last_name: str
    email: str
    provider_id: int


class UserListSchema(Schema):
    items: list[UserSchema]
