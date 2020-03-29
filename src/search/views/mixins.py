"""
Mixins for class-based views in the search app.
"""

import abc

from django.core import serializers
from django.db.models import QuerySet
from django.http import HttpResponse
from search.forms import BasicSearchForm
from search.solr import SearchEngine


class JsonResponseMixin(metaclass=abc.ABCMeta):
    """
    Mixing used to render a JSON response from database queries.
    """

    def render_to_json_response(self, context, **response_kwargs):
        """
        Return a JSON response, using 'context' to create the payload.
        """
        query_results = self.get_data(context)
        data = serializers.serialize("json", query_results)
        return HttpResponse(data, content_type="application/json", **response_kwargs)

    @abc.abstractmethod
    def get_data(self, context: dict) -> QuerySet:
        """
        Given a context, make a query to the database. Use the results of
        the query in the response.
        """
        pass


class BasicSearchMixin(metaclass=abc.ABCMeta):
    """
    Mixin for views that include the site's "basic search" functionality
    in them.
    """

    basic_search_button_name = "search"
    search_engine = SearchEngine()

    def check_basic_search(self, request) -> bool:
        """
        Check whether or not the user chose to execute a basic search.
        This function simply returns True/False based on whether or not
        the user (a) executed a GET request that (b) included the
        name of the search button in it.
        """

        return request.method == "GET" and self.basic_search_button_name in request.GET

    def create_search_form(self, request):
        """
        Return a form to display a basic search input on the page.
        """
        form = BasicSearchForm(data=request.GET)
        return form

    def execute_basic_search(self, request):
        """
        Run a basic search request. Return all compendium entries matching
        the input query.
        """

        form = self.create_search_form(request)

        # TODO: more robust error checking than this
        if form.is_valid():
            query = form.cleaned_data.get("query")
            results = self.search_engine.basic_search(query)
            print(results)
