"""
Custom widgets for the research_assistant app
"""

from django import forms


class TagCheckboxSelectMultiple(forms.CheckboxSelectMultiple):
    """
    Custom widget for selecting tags to add to a compendium entry.
    """

    template_name = "widgets/tag_checkbox_select.html"
    option_template_name = "widgets/tag_checkbox_option.html"
