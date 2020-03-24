"""
Views for the public-facing side of the site.
"""

from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from entries.models import CompendiumEntryTag, CompendiumEntry
from django.http import HttpResponse


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


@require_http_methods(["GET"])
def articles(request, slug_title):
    article = CompendiumEntry.objects.filter(slug=slug_title)
    if article.exists():
        article = article.first()
    else:
        return HttpResponse("<h1>Page not found</h1>")

    context = {"article": article}
    return render(request, "article.html", context)
