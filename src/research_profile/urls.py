from django.conf.urls import url
from research_profile.views import *
from django.urls import path, include

urlpatterns = [
    path("", researcher_profile, name="research profile"),
]
