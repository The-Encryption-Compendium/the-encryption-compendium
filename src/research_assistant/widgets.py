"""
Custom widget classes for the research_assistant app.
"""

from django import forms
from encryption_compendium.widgets import IconTextInput

"""
---------------------------------------------------
Selector-button widgets
---------------------------------------------------
"""


class TagCheckboxSelectMultiple(forms.CheckboxSelectMultiple):
    """
    Custom widget for selecting tags to add to a compendium entry.
    """

    template_name = "widgets/tag_checkbox_select.html"
    option_template_name = "widgets/tag_checkbox_option.html"


"""
---------------------------------------------------
Modified TextInput widgets
---------------------------------------------------
"""


class EmailTextInput(IconTextInput):
    """
    Custom TextInput widget that also displays an icon to indicate that the
    input is an email address.
    """

    icon_name = "envelope"
    placeholder = "user@example.com"


class URLTextInput(IconTextInput):
    """
    Custom TextInput widget that also displays an icon to indicate that the
    input is a URL.
    """

    icon_name = "link"
    placeholder = "https://example.com"
