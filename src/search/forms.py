"""
Search-related forms. Used to parse data from site visitors in order
to perform search.
"""

import re
from django import forms
from typing import List, Tuple
from utils.widgets import SearchInput


class BasicSearchForm(forms.Form):
    """
    Form for performing basic search queries. The form will validate
    its input and split it into tokens that can be used when querying
    Solr.
    """

    query = forms.CharField(
        widget=SearchInput(
            attrs={
                "class": "uk-input uk-form-large",
                "type": "search",
                "placeholder": "Search...",
            }
        )
    )

    rows = forms.IntegerField(initial=20, widget=forms.HiddenInput(), required=False,)

    page = forms.IntegerField(initial=0, widget=forms.HiddenInput(), required=False,)

    def clean_query(self):
        """
        Validate the query string and break it into multiple pieces before
        sending it off to Solr.
        """
        query = self.cleaned_data.get("query", None)

        if query is None:
            return []

        # Otherwise, we break the query into pieces and then construct
        # a query out of all of those pieces.
        #
        # Start by removing any characters from the substring that we
        # will be ignoring anyways
        query = self._strip_unused_characters(query)

        # Now tokenize the string:
        quoted_strings, remainder = self._extract_quoted_strings(query)
        words, _ = self._extract_words(remainder)

        return {
            "quoted_substrings": quoted_strings,
            "words": words,
        }

    def clean_rows(self):
        rows = self.cleaned_data.get("rows")
        if rows is None:
            return 20
        else:
            return rows

    def clean_page(self):
        page = self.cleaned_data.get("page")
        if page is None:
            return 0
        else:
            return page

    def clean(self):
        cleaned_data = super().clean()
        query_params = cleaned_data.pop("query")
        cleaned_data.update(query_params)
        return cleaned_data

    """
    Internal API
    """

    def _strip_unused_characters(self, query: str) -> str:
        """
        Remove all characters from a query string that will be ignored
        when we query Solr.

        NOTE: this function should _not_ be relied upon to clean a string
        for safety purposes, e.g. as a blacklist for certain characters.
        Instead, it is simply used to ensure that some queries aren't
        accidentally ignored for various reasons. For instance, in the query

            query = "\"hello, world!\""

        we would like to be able to extract the substring "hello, world", but
        we can't do that unless we strip exclamation marks from the string.
        """
        patt = re.compile(r"[!\{\}\(\)]")
        return patt.sub("", query)

    def _extract_quoted_strings(self, query: str) -> Tuple[List[str], str]:
        """
        Extract all substrings of the query that are enclosed within quotation
        marks. Returns the quoted substrings as well as the rest of the string
        (minus the quoted substrings).
        """
        patt = re.compile(r"\"([, \.\-\$\w\d]+)\"")
        substrs = patt.findall(query)
        remainder = patt.sub("", query)

        return substrs, remainder

    def _extract_words(self, query: str) -> Tuple[List[str], str]:
        """
        Extract all words from a query string. Returns a list of words as well
        as the rest of the string (minus the quoted substrings)
        """
        patt = re.compile(r"([\w\d\.\-\$]+)")
        words = patt.findall(query)
        remainder = patt.sub("", query)

        return words, remainder


class AdvancedSearchForm(forms.Form):
    """
    Form for performing advanced search.
    """

    search_string = forms.CharField()

    authors = forms.MultipleChoiceField()
    published_by = forms.ChoiceField()
    published_before = forms.DateField()
    published_after = forms.DateField()

    tags = forms.MultipleChoiceField()
