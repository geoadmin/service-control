from typing import Any

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType


def create_user_with_permissions(
    username: str, password: str, permissions: list[tuple[str, str, str]]
) -> Any:
    user = get_user_model().objects.create_user(username=username, password=password)
    for app_label, model, codename in permissions:
        content_type = ContentType.objects.get(app_label=app_label, model=model)
        permission = Permission.objects.get(content_type=content_type, codename=codename)
        user.user_permissions.add(permission)
    return user
