"""
User-facing views for performing search
"""

import math
import re

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
        query = request.GET.dict()
        query.setdefault("query", "")
        self.search_logger.info(f"QUERY = {query}")
        results = self.execute_basic_search(query)
        search_form = self.create_search_form(query)

        # Populate some CompendiumEntry objects with the data that we found
        # from Solr
        entries = results["response"]["docs"]
        entries = [CompendiumEntry(**entry) for entry in entries]

        hits = results["response"]["numFound"]
        rows = results["meta"]["rows"]  # Entries per page
        page = results["meta"]["page"]

        # Start/end result numbers
        start = min(results["response"]["start"] + 1, hits)
        end = results["response"]["start"] + len(entries)

        if hits == 0:
            n_pages = 0
        else:
            n_pages = math.ceil(hits / rows)

        context = {
            "query": query,
            "search_form": search_form,
            "qtime": results["responseHeader"]["QTime"],
            "hits": hits,
            "page": page,
            "n_pages": n_pages,
            "rows": rows,
            "start": start,
            "end": end,
            "entries": entries,
            "start": start,
            "rows": rows,
        }

        # Check spelling
        correctly_spelled, suggested_query = self._check_spelling(query, results)

        if not correctly_spelled:
            context["suggested_query"] = suggested_query

        return render(request, "entry_list.html", context)

    """
    Internal API
    """

    def _check_spelling(self, query: str, results: dict):
        """
        Check the spelling of the results returned by execute_basic_search.
        If the query is misspelled and there aren't many (or any) results
        returned by the query, provide spelling suggestions.

        Returns
        -------
        correctly_spelled : bool
            Whether or not the words in the query were correctly spelled.
            If no spelling mistakes where found, or there were sufficiently
            many results returned, correctly_spelled is returned as True.

        suggested_query : Optional[str]
            A suggested query to replace the input query. Returns as None
            if no suggested query could be generated.
        """

        self.search_logger.info(results)

        hits = results["response"]["numFound"]
        correctly_spelled = results.get("spellcheck", {}).get("correctlySpelled", True)
        correctly_spelled = correctly_spelled or hits > 10

        if correctly_spelled:
            return correctly_spelled, None

        # Create a "suggested query" by trying to fix every misspelled word
        # that was found.
        s = results.get("spellcheck", {}).get("suggestions", [])
        if len(s) == 0:
            return correctly_spelled, None

        suggestions = [(s[ii], s[ii + 1]) for ii in range(len(s) // 2)]
        for (word, suggestion) in suggestions:
            # Find the top-suggested replacement and use regex to replace it
            # in the query.
            replacement = suggestion["suggestion"][0]["word"]
            query = re.sub(f"\\b{word}\\b", replacement, query, flags=re.IGNORECASE)

        return correctly_spelled, query
