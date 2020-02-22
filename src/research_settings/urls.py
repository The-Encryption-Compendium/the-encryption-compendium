from django.conf.urls import url
from research_settings.views import *
from django.urls import path, include

urlpatterns = [
    path("", research_settings, name="research settings"),
]
