"""
Search-related forms. Used to parse data from site visitors in order
to perform search.
"""

from django import forms


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
