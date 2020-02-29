"""
Views for the public-facing side of the site.
"""

from django.shortcuts import render
from django.views.decorators.http import require_http_methods


@require_http_methods(["GET"])
def landing_page(request):
    return render(request, "landing_page.html")
