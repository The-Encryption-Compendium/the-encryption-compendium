from django.conf.urls import url
from django.contrib.auth import views as auth_views
from django.urls import path, include
from research_assistant.views import *
from research_settings import urls as settings_urls
from research_profile import urls as profile_url

urlpatterns = [
    url(r"^add-user", add_new_user, name="add new user"),
    url(r"^sign-up", sign_up, name="sign up"),
    url(r"^dashboard", research_dashboard, name="research dashboard"),
    url(r"^login", research_login, name="research login"),
    url(r"^logout", research_logout, name="research logout"),
    url(r"^new-article", NewCompendiumEntryView.as_view(), name="research new article"),
    url(r"^new-tag", research_add_tag, name="research add tag"),
    path("my-entries/", research_my_entries, name="research my entries"),
    path("list-my-entries/", research_list_my_entries, name="list my entries"),
    url(r"edit-entries$", EditCompendiumEntryView.as_view(), name="edit my entries"),
    url(
        r"edit-entries/(?P<id>[0-9]+)",
        EditCompendiumEntryView.as_view(),
        name="edit my entries",
    ),
    path("settings/", include(settings_urls)),
    path("profile/", include(profile_url)),
]
