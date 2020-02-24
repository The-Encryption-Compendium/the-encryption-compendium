"""
Custom widget classes for use across the project.
"""

from django import forms

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
