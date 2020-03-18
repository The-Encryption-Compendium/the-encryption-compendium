"""encryption_compendium URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
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
from django.conf import settings
from django.conf.urls import url, include
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import path, reverse
from django.views.generic.base import RedirectView
from public_view import views as pubviews
from search import urls as search_urls
from research_assistant import urls as research_urls

urlpatterns = [
    ### Admin view
    path("admin/", admin.site.urls),
    ### URLs for the research_assistant app
    url(r"^research/", include(research_urls)),
    ### URLs for the public-facing views
    url(r"^$", pubviews.landing_page, name="landing page"),
    ### URLs for search
    url(r"^search", include(search_urls)),
]

if settings.DEBUG:
    # Serve static files from the Django/Gunicorn server during development
    urlpatterns += staticfiles_urlpatterns()
