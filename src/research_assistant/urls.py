from django.conf.urls import url
from research_assistant.views import *
from django.urls import path

urlpatterns = [
    url(r"^login", research_login, name="research login"),
    url(r"^logout", research_logout, name="research logout"),
    url(r"^dashboard", research_dashboard, name="research dashboard"),
    url(r"^new_article", research_new_article, name="research new article"),
    url(r"^new_tag", research_add_tag, name="research add tag"),
]
