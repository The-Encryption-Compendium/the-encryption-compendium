"""
Views for the public-facing side of the site.
"""

from django.http import HttpResponse
from django.shortcuts import render
from django.views import View
from django.views.decorators.http import require_http_methods
from entries.models import CompendiumEntryTag, CompendiumEntry
from search.views.mixins import BasicSearchMixin


class LandingPage(BasicSearchMixin, View):
    """
    Displays the landing page of the site. Includes a search form so
    that users can immediately start searching the compendium.
    """

    def get(self, request):
        search_form = self.create_search_form(request)
        tags = CompendiumEntryTag.objects.order_by("tagname").all()
        return render(
            request,
            "landing_page.html",
            context={"tags": tags, "search_form": search_form},
        )


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


@require_http_methods(["GET"])
def articles(request, slug_title):
    article = CompendiumEntry.objects.filter(slug=slug_title)
    if article.exists():
        article = article.first()
    else:
        return HttpResponse("<h1>Page not found</h1>")

    context = {"article": article}
    return render(request, "article.html", context)
