"""
Mixins for class-based views in the search app.
"""

import abc
import json

from django.core import serializers
from django.db.models import QuerySet
from django.http import HttpResponse
from search.forms import BasicSearchForm
from search.solr import SearchEngine
from typing import Dict, Optional, Union

"""
Definitions for JSON REST API
"""


class JsonAPIError(Exception):
    """
    An exception that should be thrown whenever there's an error making
    a request to the site's REST API.
    """

    def __init__(self, msg: str, *args, status_code: int = 400, **kwargs):
        super().__init__(msg, *args, **kwargs)
        self.status_code = status_code


class JsonResponseMixin(metaclass=abc.ABCMeta):
    """
    Mixin used to render a JSON response from database queries.
    """

    def render_to_json_response(
        self, get_params: dict, context: Optional[dict] = None,
    ):
        """
        Return a JSON response, using 'context' to create the payload.
        """

        try:
            status_code = 200

            if context is not None:
                query_results = self.get_data(get_params, context=context)
            else:
                # Don't pass in the context kwarg so that child classes
                # can use their own defaults.
                query_results = self.get_data(get_params)

            if isinstance(query_results, QuerySet):
                query_results = serializers.serialize("json", query_results)
            elif isinstance(query_results, str):
                # Assume that the string is already JSON-formatted
                pass
            else:
                query_results = json.dumps(query_results)

        except JsonAPIError as ex:
            # Error processing the query
            status_code = ex.status_code
            query_results = json.dumps({"error": str(ex)})

        return HttpResponse(
            query_results, content_type="application/json", status=status_code,
        )

    @abc.abstractmethod
    def get_data(
        self, get_params: dict, context: Optional[dict] = None,
    ) -> Union[Dict, QuerySet, str]:
        """
        Given a context, make a query to the database. Use the results of
        the query in the response.
        """
        pass


"""
Search mixins
"""


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

    def execute_basic_search(self, params):
        """
        Run a basic search request. Return all compendium entries matching
        the input query.
        """

        form = BasicSearchForm(data=params)

        # TODO: more robust error checking
        if form.is_valid():
            results = self.search_engine.basic_search(form.cleaned_data)
        else:
            raise Exception(str(form.errors))

        return results
