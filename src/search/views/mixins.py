"""
Mixins for class-based views in the search app.
"""

import abc

from django.core import serializers
from django.db.models import QuerySet
from django.http import HttpResponse


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
