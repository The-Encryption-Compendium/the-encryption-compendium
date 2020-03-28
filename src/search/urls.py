from django.conf.urls import url
from search.views import FullCompendiumView, SearchView

urlpatterns = [
    url(r"^$", SearchView.as_view(), name="search"),
    url(r"_all", FullCompendiumView.as_view()),
]
