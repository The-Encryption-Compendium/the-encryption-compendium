"""
User-facing views for performing search
"""

import math

from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from django.views import View
from entries.models import CompendiumEntry
from search.views.mixins import BasicSearchMixin


class SearchView(BasicSearchMixin, View):
    """
    Displays all of the compendium entries that appear as the result of a query.
    """

    default_pagination = 10

    def get(self, request):
        results = self.execute_basic_search(request.GET)

        query = request.GET.get("query", None)

        # Populate some CompendiumEntry objects with the data that we found
        # from Solr
        entries = [CompendiumEntry(**entry) for entry in results.docs]

        hits = results.hits
        rows = results.rows  # Entries per page
        page = results.page

        # Start/end result numbers
        start = results.start + 1
        end = results.start + len(entries)

        if hits == 0:
            n_pages = 0
        else:
            n_pages = math.ceil(hits / rows)

        context = {
            "hits": hits,
            "page": page,
            "n_pages": n_pages,
            "rows": rows,
            "start": start,
            "end": end,
            "entries": entries,
            "query": query,
            "start": start,
            "rows": rows,
        }
        return render(request, "entry_list.html", context)

    def get_old(self, request):
        entries = CompendiumEntry.objects.all()

        # Paginate (don't show all of the results on a single page)
        paginator = Paginator(entries, self.default_pagination)
        page_obj = paginator.get_page(request.GET.get("page"))
        page_number = page_obj.number

        context = {
            "page_obj": page_obj,
        }
        return render(request, "entry_list.html", context)
