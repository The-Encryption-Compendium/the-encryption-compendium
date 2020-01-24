from django.conf.urls import url
from research_assistant.views import *

urlpatterns = [
    url(r"^login", research_login, name="research login"),
    url(r"^dashboard", research_dashboard, name="research dashboard"),
]
