"""
Custom widget classes for the research_assistant app.
"""

import os

from django import forms
from encryption_compendium.utils import months
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

    template_name = os.path.join("widgets", "tag_checkbox_select.html")
    option_template_name = os.path.join("widgets", "tag_checkbox_option.html")


"""
---------------------------------------------------
Widgets related to choosing dates
---------------------------------------------------
"""


class DayWidget(forms.Select):
    """
    A widget for selecting the day
    """

    def days():
        """
        Get a list of all of the available values of 'day'.
        """
        return list(range(0, 32))

    def day_choices():
        """
        Get a list of all of the value-label pairs for 'day'.
        """
        days = DayWidget.days()
        choices = [(0, "")]
        choices += list((d, d) for d in days[1:])
        return choices

    def __init__(self, *args, **kwargs):
        choices = DayWidget.day_choices()
        kwargs["choices"] = choices
        super().__init__(*args, **kwargs)


class MonthWidget(forms.Select):
    """
    A widget for selecting the month.
    """

    _months = ["", *months()]

    def months(self):
        """
        Get all of the available values of "month". Includes an empty string
        (corresponding to no month being selected).
        """
        return MonthWidget._months

    def month_choices(self):
        """
        Get all of the available value-label pairs for the "month" parameter.
        """
        return [c for c in enumerate(self.months())]

    def __init__(self, *args, **kwargs):
        # Need to account for cases in which no month is selected
        choices = self.month_choices()
        kwargs["choices"] = choices
        super().__init__(*args, **kwargs)


class YearWidget(forms.TextInput):
    """
    A widget for selecting the year
    """

    pass


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
