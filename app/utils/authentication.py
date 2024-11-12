from typing import Any

from ninja.errors import HttpError
from ninja.security.session import SessionAuth

from django.http import HttpRequest


class PermissionAuth(SessionAuth):
    """ Ninja authentication that extends the session authentication with permission checks. """

    def __init__(self, permission: str, csrf: bool = True) -> None:
        super().__init__(csrf)
        self.permission = permission

    def authenticate(self, request: HttpRequest, key: str | None) -> None | Any:
        user = super().authenticate(request, key)
        if user is not None and not user.has_perm(self.permission):
            raise HttpError(403, "Forbidden")
        return user
