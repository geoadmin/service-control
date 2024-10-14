from ninja import Schema
from pydantic import EmailStr


class UserSchema(Schema):

    username: str
    first_name: str
    last_name: str
    email: EmailStr
    provider_id: int


class UserListSchema(Schema):
    items: list[UserSchema]
