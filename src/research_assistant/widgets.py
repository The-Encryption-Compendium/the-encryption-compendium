"""
Custom widgets for the research_assistant app
"""

from django import forms


class URLTextInput(forms.TextInput):
    """
    Custom TextInput widget that also displays an icon to indicate that the
    input is a URL.
    """

    template_name = "widgets/url_input.html"


class TagCheckboxSelectMultiple(forms.CheckboxSelectMultiple):
    """
    Custom widget for selecting tags to add to a compendium entry.
    """

    template_name = "widgets/tag_checkbox_select.html"
    option_template_name = "widgets/tag_checkbox_option.html"
