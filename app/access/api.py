from ninja import Router
from provider.models import Provider

from django.http import HttpRequest
from django.shortcuts import get_object_or_404

from .models import User
from .schemas import UserListSchema
from .schemas import UserSchema

router = Router()


def user_to_response(model: User) -> UserSchema:
    """
    Maps the given model to the corresponding schema.
    """
    response = UserSchema(
        username=model.username,
        first_name=model.first_name,
        last_name=model.last_name,
        email=model.email,
        provider_id=model.provider.id,
    )
    return response


@router.get("users/{username}", response={200: UserSchema}, exclude_none=True)
def user(request: HttpRequest, username: str) -> UserSchema:
    """
    Get the user with the given username.
    """
    model = get_object_or_404(User, username=username)
    response = user_to_response(model)
    return response


@router.get("users", response={200: UserListSchema}, exclude_none=True)
def users(request: HttpRequest) -> dict[str, list[UserSchema]]:
    """
    Get all users.
    """
    models = User.objects.all()
    responses = [user_to_response(model) for model in models]
    return {"items": responses}


@router.post("users", response={201: UserSchema})
def create_user(request: HttpRequest, user_in: UserSchema) -> UserSchema:
    """Create the given user and return it.

    Return HTTP status code

        - 201 (Created) if the User was created as expected
        - 404 (Not Found) if there is no provider with the given provider ID
        - 409 (Conflict) if there is already a record with the same username
        - 422 (Unprocessable Content) if there is any other invalid value
    """
    provider = get_object_or_404(Provider, id=user_in.provider_id)

    user_out = User.objects.create(
        username=user_in.username,
        first_name=user_in.first_name,
        last_name=user_in.last_name,
        email=user_in.email,
        provider=provider
    )
    return user_to_response(user_out)
