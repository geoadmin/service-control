"""
URL configuration for app project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from admin import views

from django.conf import settings
from django.contrib import admin
from django.urls import path

from .api import api
from .api import root

customAdminUrls = []
if settings.ENABLE_OAUTH2_PROXY:
    customAdminUrls = [
        path(
            settings.API_PATH_PREFIX + 'admin/logout/',
            views.custom_admin_logout,
            name='custom_admin_logout'
        ),
        # Add a new login endpoint for oauth2 login
        path(
            settings.API_PATH_PREFIX + 'admin/oauth2/login/',
            views.custom_admin_login,
            name='custom_admin_login'
        ),
    ]

urlpatterns = [
    path(settings.API_PATH_PREFIX + '', root.urls),
    path(settings.API_PATH_PREFIX + 'api/v1/', api.urls),
    # NOTE: the following 2 endpoints needs to be registered before the admin interface endpoints
    # overwrite the default django admin/logout endpoint
    *customAdminUrls,
    path(settings.API_PATH_PREFIX + 'admin/', admin.site.urls),
]
