from ninja import Router

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
        id=model.id,
        first_name=model.first_name,
        last_name=model.last_name,
        email=model.email,
        provider_id=model.provider.id,
    )
    return response


@router.get("users/{user_id}", response={200: UserSchema}, exclude_none=True)
def user(request: HttpRequest, user_id: int) -> UserSchema:
    """
    Get the user with the given ID.
    """
    model = get_object_or_404(User, id=user_id)
    response = user_to_response(model)
    return response


@router.get("users", response={200: UserListSchema}, exclude_none=True)
def users(request: HttpRequest) -> dict[str, list[UserSchema]]:
    """
    Get all users.
    """
    models = User.objects.order_by("id").all()
    responses = [user_to_response(model) for model in models]
    return {"items": responses}
