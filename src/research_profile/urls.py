from django.conf.urls import url
from research_profile.views import *
from django.urls import path, include

urlpatterns = [
    path("", research_profile, name="research profile"),
    path("my_entries/", research_my_entries, name="research my entries"),
]
