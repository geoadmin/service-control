import logging
import urllib

from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import logout
from django.http import HttpRequest
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse

logger = logging.getLogger(__name__)


def custom_admin_login(request: HttpRequest) -> HttpResponse:
    # Redirect URL after successful login
    redirect_uri = f"{request.build_absolute_uri(reverse('admin:index'))}"

    oauth2_proxy_login_url = \
        f"https://{settings.OAUTH2_PROXY_DOMAIN}/oauth2/start?" + \
        f"rd={urllib.parse.quote(redirect_uri)}"

    return redirect(oauth2_proxy_login_url)


@staff_member_required
def custom_admin_logout(request: HttpRequest) -> HttpResponse:
    # logout the user from Django
    logout(request)

    # Redirect to the django admin login page after logout
    redirect_after_logout = f'{request.build_absolute_uri(reverse("admin:login"))}'

    # We need to log out from Cognito and OAuth2 Proxy
    # We also needs to tell cognito to which url it needs to redirect after logout
    cognito_logout_url = f'{settings.COGNITO_DOMAIN_URL}/logout?' + \
        f'client_id={settings.COGNITO_OAUTH2_PROXY_APP_CLIENT_ID}&' + \
        f'logout_uri={urllib.parse.quote_plus(redirect_after_logout)}'
    oauth_proxy_logout_url = f'https://{settings.OAUTH2_PROXY_DOMAIN}/oauth2/sign_out?' + \
        f'rd={urllib.parse.quote_plus(cognito_logout_url)}'

    return redirect(oauth_proxy_logout_url)
