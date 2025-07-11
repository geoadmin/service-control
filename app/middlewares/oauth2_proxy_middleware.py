import logging
from typing import Callable

from django.contrib.auth import get_user
from django.contrib.auth.middleware import RemoteUserMiddleware
from django.contrib.auth.models import Group
from django.http import HttpRequest
from django.http import HttpResponse

logger = logging.getLogger(__name__)


class Oauth2ProxyRemoteUserMiddleware(RemoteUserMiddleware):
    header = "HTTP_X_AUTH_REQUEST_USER"


class Oauth2ProxyRemoteGroupMiddleware:
    header = "HTTP_X_AUTH_REQUEST_GROUPS"

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request: HttpRequest) -> HttpResponse:
        # Code to be executed for each request before
        # the view (and later middleware) are called.

        try:
            raw_groups = request.META[self.header]
        except KeyError as error:
            logger.error("Failed to get group header: %s", error)
            return self.get_response(request)

        user = get_user(request)
        if not user.is_authenticated:
            return self.get_response(request)

        group_names = [g.strip() for g in raw_groups.split(",") if g.strip()]
        if not group_names:
            return self.get_response(request)

        for name in group_names:
            Group.objects.get_or_create(name=name)

        user.groups.set(Group.objects.filter(name__in=group_names))
        if "ppbgdi-admin" in group_names:
            user.is_staff = True
            user.is_superuser = True
        user.save()

        return self.get_response(request)
