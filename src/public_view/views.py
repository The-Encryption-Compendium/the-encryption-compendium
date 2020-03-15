"""
Views for the public-facing side of the site.
"""

from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from research_assistant.models import CompendiumEntryTag


@require_http_methods(["GET"])
def landing_page(request):
    """
    Landing page for the website.
    """
    tags = CompendiumEntryTag.objects.order_by("tagname").all()
    return render(request, "landing_page.html", context={"tags": tags})


@require_http_methods(["GET"])
def basic_search(request):
    """
    Get a list of all of the compendium entries that match a particular
    combination of tags.
    """
    # tag_ids = request.GET(
    return render(request, "landing_page.html")


@require_http_methods(["POST"])
def advanced_search(request):
    return render(request, "advanced_search.html")
