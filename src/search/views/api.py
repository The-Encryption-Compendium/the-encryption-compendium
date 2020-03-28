"""
REST API for searching the compendium.
"""

import abc

from .mixins import JsonResponseMixin
from django.views.generic import TemplateView
from entries.models import CompendiumEntry


class JSONView(JsonResponseMixin, TemplateView, metaclass=abc.ABCMeta):
    """
    Abstract class for views that return JSON as their output.
    """

    def render_to_response(self, context, **response_kwargs):
        return self.render_to_json_response(context, **response_kwargs)


class FullCompendiumView(JSONView):
    """
    Retrieve the entire compendium in a JSON response.
    """

    def get_data(self, context):
        return CompendiumEntry.objects.all()
