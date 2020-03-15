"""
Views for the public-facing side of the site.
"""

from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from research_assistant.models import CompendiumEntryTag


@require_http_methods(["GET"])
def landing_page(request):
    # Get a list of all of the tags, sorted alphabetically
    tags = CompendiumEntryTag.objects.order_by("tagname").all()
    return render(request, "landing_page.html", context={"tags": tags})


@require_http_methods(["POST"])
def advanced_search(request):
    return render(request, "advanced_search.html")
