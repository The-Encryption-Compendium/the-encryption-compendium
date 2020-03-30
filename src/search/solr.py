"""
Code for integrating with Apache Solr for search on the site
"""

import pysolr

from typing import Dict, List


class SearchEngine:
    """
    Wrapper around the pysolr.Solr class to make it easier to connect
    to and query Apache Solr.
    """

    def __init__(self):
        self.solr = pysolr.Solr(
            "http://tec-search:8983/solr/compendium", always_commit=False
        )

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

        # Combine tokens into a single search query for Solr
        query_str = " && ".join(f"basic_search:{T!r}" for T in tokens)

        # Add pagination
        kwargs = {
            "rows": query.get("results_per_page", 20),
            "start": query.get("page", 0),
        }

        return self.solr.search(query_str, **kwargs)
