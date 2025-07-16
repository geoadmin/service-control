import logging
from typing import Callable

from django.conf import settings
from django.contrib.auth import get_user
from django.contrib.auth.middleware import RemoteUserMiddleware
from django.contrib.auth.models import Group
from django.http import HttpRequest
from django.http import HttpResponse

logger = logging.getLogger(__name__)


class Oauth2ProxyRemoteUserMiddleware(RemoteUserMiddleware):
    header = "HTTP_X_AUTH_REQUEST_USER"


class Oauth2ProxyRemoteMiddleware:
    group_header = "HTTP_X_AUTH_REQUEST_GROUPS"
    preferred_username_header = "HTTP_X_AUTH_REQUEST_PREFERRED_USERNAME"
    email_header = "HTTP_X_AUTH_REQUEST_EMAIL"

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request: HttpRequest) -> HttpResponse:
        # Code to be executed for each request before
        # the view (and later middleware) are called.

        user = get_user(request)
        if not user.is_authenticated:
            # If the user is not authenticated then do nothing and let django
            # refuse the request
            return self.get_response(request)

        # If the user is authenticated then we need to update it with the following oauth2-proxy
        # provided user information:
        #  - preferred_username
        #  - email
        #  - groups
        try:
            preferred_username = request.META[self.preferred_username_header].strip()
        except KeyError as error:
            logger.error("Failed to get preferred_username header: %s", error)
            return self.get_response(request)

        try:
            email = request.META[self.email_header].strip()
        except KeyError as error:
            logger.error("Failed to get email header: %s", error)
            return self.get_response(request)

        try:
            raw_groups = request.META[self.group_header]
        except KeyError as error:
            logger.error("Failed to get group header: %s", error)
            return self.get_response(request)

        group_names = [g.strip() for g in raw_groups.split(",") if g.strip()]
        if not group_names:
            return self.get_response(request)

        for name in group_names:
            Group.objects.get_or_create(name=name)

        # Django user.first_name is used as display in the admin interface, therefore set it
        # as preferred user name.
        user.first_name = preferred_username
        user.email = email
        user.groups.set(Group.objects.filter(name__in=group_names))

        # Check if the user is allowed in django admin interface
        if bool(set(group_names) & set(settings.OAUTH2_PROXY_DJANGO_ADMIN_GROUPS)):
            user.is_staff = True
            user.is_superuser = True
        user.save()

        return self.get_response(request)
