from django.conf.urls import url
from django.contrib.auth import views as auth_views
from django.urls import path, include
from public_view.views import articles

urlpatterns = [
    path("<slug:slug_title>/", articles),
]
