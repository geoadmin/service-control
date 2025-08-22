from http import HTTPStatus

from ninja import Router
from ninja.errors import HttpError
from provider.models import Provider
from utils.authentication import PermissionAuth

from django.http import HttpRequest
from django.http import HttpResponse
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
        provider_id=model.provider.provider_id,
    )
    return response


@router.get(
    "users/{username}",
    response={200: UserSchema},
    exclude_none=True,
    auth=PermissionAuth("access.view_user"),
)
def user(request: HttpRequest, username: str) -> UserSchema:
    """
    Get the user with the given username.
    """
    model = get_object_or_404(User.objects, username=username)
    response = user_to_response(model)
    return response


@router.get(
    "users",
    response={200: UserListSchema},
    exclude_none=True,
    auth=PermissionAuth("access.view_user"),
)
def users(request: HttpRequest) -> dict[str, list[UserSchema]]:
    """
    Get all users.
    """
    models = User.objects.all()
    responses = [user_to_response(model) for model in models]
    return {"items": responses}


@router.post(
    "users", response={201: UserSchema}, auth=PermissionAuth("access.add_user")
)
def create(request: HttpRequest, user_in: UserSchema) -> UserSchema:
    """Create the given user and return it.

    Return HTTP status code

        - 201 (Created) if the User was created as expected
        - 404 (Not Found) if there is no provider with the given provider ID
        - 409 (Conflict) if there is already a record with the same username
        - 422 (Unprocessable Content) if there is any other invalid value
        - 500 (Internal Server Error) if there is inconsistency with cognito
        - 503 (Service Unavailable) if cognito cannot be reached
    """
    provider = get_object_or_404(Provider, provider_id=user_in.provider_id)

    user_out = User.objects.create(
        username=user_in.username,
        first_name=user_in.first_name,
        last_name=user_in.last_name,
        email=user_in.email,
        provider=provider,
    )
    return user_to_response(user_out)


@router.delete("users/{username}", auth=PermissionAuth("access.delete_user"))
def delete(request: HttpRequest, username: str) -> HttpResponse:
    """
    Delete the user with the given username.

    Return HTTP status code
    - 204 (No Content) if the user has been deleted
    - 404 (Not Found) if there is no user with the given username
    - 500 (Internal Server Error) if there is inconsistency with cognito
    - 503 (Service Unavailable) if cognito cannot be reached
    """
    user_to_delete = get_object_or_404(User, username=username)
    user_to_delete.disable()
    return HttpResponse(status=204)


@router.put("users/{username}", auth=PermissionAuth("access.change_user"))
def update_user(
    request: HttpRequest, username: str, user_in: UserSchema
) -> HttpResponse | UserSchema:
    """Update the given user with the given user data and return it.

    Return HTTP status code
    - 200 (OK) if the user has been updated successfully
    - 400 (Bad Request) if there is no provider with the given ID
    - 404 (Not Found) if there is no user with the given username
    - 500 (Internal Server Error) if there is an inconsistency with Cognito
    - 503 (Service Unavailable) if Cognito cannot be reached
    """
    user_object = get_object_or_404(User, username=username)

    provider = Provider.objects.filter(provider_id=user_in.provider_id).first()
    if not provider:
        raise HttpError(HTTPStatus.BAD_REQUEST, "Provider does not exist")

    user_object.username = user_in.username
    user_object.first_name = user_in.first_name
    user_object.last_name = user_in.last_name
    user_object.email = user_in.email
    user_object.provider_id = provider.id
    user_object.save()

    return user_to_response(user_object)
