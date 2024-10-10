from ninja import Schema


class UserSchema(Schema):

    id: int
    first_name: str
    last_name: str
    email: str
    provider_id: int
