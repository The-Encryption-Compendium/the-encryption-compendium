"""
Custom widget classes.
"""

from django import forms

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


class IconTextInput(forms.TextInput):
    """
    Custom TextInput widget that also displays an icon to indicate the type
    of input that should be provided.
    """

    template_name = "widgets/icon_input.html"

    def get_context(self, *args):
        context = super().get_context(*args)

        # Add a field "icon_name" to the context
        try:
            context["widget"].setdefault("icon_name", self.icon_name)
        except AttributeError:
            pass

        # Define a default placeholder
        try:
            context["widget"]["attrs"].setdefault("placeholder", self.placeholder)
        except AttributeError:
            pass

        return context


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
