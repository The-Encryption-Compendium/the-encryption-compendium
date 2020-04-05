"""
Code for integrating with Apache Solr for search on the site
"""

import logging
import requests
from typing import Dict, List


class SearchEngine:
    """
    Wrapper around the pysolr.Solr class to make it easier to connect
    to and query Apache Solr.
    """

    solr_logger = logging.getLogger("search.solr")

    def __init__(self):
        self.solr_url = "http://tec-search:8983/solr/compendium"

    """
    Search functions
    """

    def basic_search(self, query: Dict[str, List[str]]):
        """
        Make a query for a string against multiple fields in the Solr schema using
        a tokenized query string.
        """

        tokens = query.get("quoted_substrings", [])
        tokens += query.get("words", [])

        # If tokens == [], we assume that we didn't receive any words at all,
        # in which case we'll simply match everything in the compendium.
        if len(tokens) == 0:
            tokens = [""]

        # Combine tokens into a single search query for Solr
        query_str = " && ".join(f"basic_search:*{T}*" for T in tokens)

        # Add pagination
        page = query.get("page", 0)
        rows = query.get("rows", 20)
        start = page * rows
        data = {
            "q": query_str,
            "rows": rows,
            "start": start,
            "fl": "id,title,abstract,slug,year,month,day",
        }

        req = requests.get(f"{self.solr_url}/spell", params=data)
        results = req.json()

        # Add some more useful data to the results dictionary
        results["meta"] = {
            "page": page,
            "rows": rows,
        }

        # Do some logging to record the transaction
        qtime = results["responseHeader"]["QTime"]
        self.solr_logger.info(f"Solr query: {query_str}")
        self.solr_logger.debug(
            f"Solr query metadata: qtime={qtime}ms queryurl={req.url}"
        )

        return results
