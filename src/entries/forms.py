"""
Forms related to creating, modifying, and deleting compendium entries.
"""

import datetime

from django import forms
from django.utils.translation import gettext as _
from entries.models import (
    CompendiumEntry,
    CompendiumEntryTag,
)
from research_assistant.widgets import *


class CompendiumEntryForm(forms.ModelForm):
    """
    CompendiumEntryForm allows users to create and modify compendium entries by
    setting each of their fields, one-by-one.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Display the tags sorted by their tag names
        self.fields["tags"].widget.choices.queryset = self.fields[
            "tags"
        ].widget.choices.queryset.order_by("tagname")

    class Meta:
        model = CompendiumEntry
        fields = (
            "title",
            "abstract",
            "url",
            "tags",
            "publisher_text",
            "year",
            "month",
            "day",
        )

        widgets = {
            "title": forms.TextInput(attrs={"class": "uk-input uk-form-width-large"}),
            "abstract": forms.Textarea(
                attrs={"class": "uk-form-width-large uk-width-1-1 uk-textarea",},
            ),
            "url": URLTextInput(attrs={"class": "uk-form-width-large uk-input"}),
            "tags": TagCheckboxSelectMultiple(
                attrs={
                    "ul_class": "uk-grid uk-grid-small uk-child-width-1-3@m",
                    "class": "uk-checkbox",
                },
            ),
            "publisher_text": forms.TextInput(
                attrs={"class": "uk-form-width-large uk-input"}
            ),
            "day": DayWidget(),
            "month": MonthWidget(),
            "year": YearWidget(),
        }

        labels = {"url": "URL", "publisher_text": "Publisher"}

        help_texts = {
            "title": "Enter the title of the new entry.",
            "url": "A link to the resource.",
            "tags": (
                """
                Choose some tags to label the new compendium entry. Tags can be used
                to help users filter through entries more easily.
                """
            ),
        }

    def clean_day(self):
        day = self.cleaned_data.get("day")
        if day == 0:
            return None
        else:
            return day

    def clean_month(self):
        month = self.cleaned_data.get("month")
        if month == 0:
            return None
        else:
            return month

    def clean(self):
        """
        Ensure that the following conditions hold on the form's input before
        validating:
        - The new entry must have at least one tag selected.
        - If the day of publication is specified, the month and year must also
          be specified.
        - If the month of publication is specified, then the year must also be
          specified.
        - If day + month + year are all specified, then the actual date that
          is chosen should be a valid date.
        """
        cleaned_data = super().clean()

        # Check that at least one tag has been selected
        tags = cleaned_data.get("tags")

        if not tags or len(tags) == 0:
            error = forms.ValidationError(
                _("At least one tag must be specified."), code="invalid_tags",
            )
            self.add_error("tags", error)

        ### Check conditions on the day-month-year fields
        day = cleaned_data.get("day")
        month = cleaned_data.get("month")
        year = cleaned_data.get("year")

        if day is not None:
            # Day specified => month and year specified
            if month is None or year is None:
                error = forms.ValidationError(
                    _(
                        "The month and year of publication must both be specified if "
                        "the day is specified."
                    ),
                    code="invalid_date",
                )
                self.add_error("day", error)

            # Day + month + year specified => date is valid
            else:
                try:
                    datetime.date(year=year, month=month, day=day)
                except:
                    error = forms.ValidationError(
                        _("We were unable to read the date you entered."),
                        code="invalid_date",
                    )
                    self.add_error("day", error)

        # Month specified => year specified
        elif month is not None and year is None:
            error = forms.ValidationError(
                _(
                    "The year of publication must be specified if the month "
                    "is specified."
                ),
                code="invalid_date",
            )
            self.add_error("month", error)

        return cleaned_data


class NewTagForm(forms.ModelForm):
    """
    NewTagForm allows the creation of new tags. It is a ModelForm based off
    of the CompendiumEntryTag model.
    """

    class Meta:
        model = CompendiumEntryTag
        fields = ("tagname",)

        labels = {"tagname": "Tag name"}

        widgets = {
            "tagname": forms.TextInput(attrs={"class": "uk-input"}),
        }

    def clean_tagname(self):
        """
        Clean function for the tagname. Ensures that the tagname is converted
        to lowercase before being saved in the database.
        """
        tagname = self.cleaned_data.get("tagname")
        if tagname:
            tagname = tagname.lower()
        return tagname


class EntryDeleteForm(forms.Form):
    """
    Form for deleting compendium entries. The form accepts the ID of an entry
    and deletes the form with that ID.
    """

    entry_id = forms.IntegerField()

    def clean(self):
        cleaned_data = super().clean()
        entry_id = cleaned_data.get("entry_id")

        return cleaned_data
