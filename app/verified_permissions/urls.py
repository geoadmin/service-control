from django.urls import path
from .api import api

urlpatterns = [path("test-vp/", api.urls)]
