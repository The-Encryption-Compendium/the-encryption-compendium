from django.conf.urls import url
from search.views import BasicSearchAPIView, FullCompendiumView, SearchView

urlpatterns = [
    url(r"^$", SearchView.as_view(), name="search"),
    url(r"_all", FullCompendiumView.as_view()),
    url(r"_basic", BasicSearchAPIView.as_view()),
]
