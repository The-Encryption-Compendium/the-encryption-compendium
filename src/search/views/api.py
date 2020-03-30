"""
REST API for searching the compendium.
"""

import abc

from .mixins import JsonAPIError, JsonResponseMixin, BasicSearchMixin
from django.views.generic import View, TemplateView
from entries.models import CompendiumEntry
from search.solr import SearchEngine

"""
Abstract classes
"""


class JsonView(JsonResponseMixin, View, metaclass=abc.ABCMeta):
    """
    Abstract class for views that return JSON as their output.
    """

    def get(self, request):
        return self.render_to_json_response(request.GET)


"""
Concrete child classes
"""


class FullCompendiumView(JsonView):
    """
    Retrieve the entire compendium in a JSON response.
    """

    def get_data(self, *args, **kwargs):
        return CompendiumEntry.objects.all()


class BasicSearchAPIView(BasicSearchMixin, JsonView):
    """
    Run basic search against Solr and get results as JSON.
    """

    search_engine = SearchEngine()

    def get_data(self, get_params, **kwargs):
        query = get_params.get("query", None)
        if query is None:
            raise JsonAPIError("'query' parameter missing", status_code=422)

        results = self.execute_basic_search(get_params)
        results = list(results)

        return results
