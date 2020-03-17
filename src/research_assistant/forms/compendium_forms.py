"""
Forms related to creating, modifying, and deleting compendium entries.
"""

import bibtexparser
import datetime

from bibtexparser.bparser import BibTexParser
from django import forms
from django.utils.translation import gettext as _
from research_assistant.models import (
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
            "title": forms.TextInput(attrs={"class": "uk-form-width-large"}),
            "abstract": forms.Textarea(
                attrs={"class": "uk-form-width-large uk-width-1-1",},
            ),
            "url": URLTextInput(attrs={"class": "uk-form-width-large"}),
            "tags": TagCheckboxSelectMultiple(
                attrs={"ul_class": "uk-grid uk-grid-small uk-grid-width-medium-1-3"},
            ),
            "publisher_text": forms.TextInput(attrs={"class": "uk-form-width-large"}),
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


class BibTexUploadForm(forms.Form):
    """
    BibTexUploadForm is an input form that allows adding new compendium entries
    to the site by either entering BibTeX manually, or uploading a .bib file.

    Fields
    ------
    bibtex_file : forms.FileField
        A form field that accepts a .bib file and parses BibTeX from that file.

    bibtex_entry : forms.CharField
        A form field that accepts raw BibTeX as text and parses it so that it
        can be converted to a list of compendium entries.
    """

    # Form field that can be used to upload a .bib file
    bibtex_file = forms.FileField(required=False, max_length=5e6,)  # 5 Mb

    # Form field to directly paste in BibTex
    bibtex_entry = forms.CharField(
        widget=forms.Textarea(
            attrs={
                "class": "monospace uk-width-1-1",
                "placeholder": "Copy BibTex here...",
            }
        ),
        required=False,
    )

    """
    Validation functions
    """

    def clean_bibtex_file(self):
        bibfile = self.cleaned_data.get("bibtex_file")

        if bibfile is None:
            return None

        else:
            try:
                parser = BibTexParser(common_strings=True)
                bib_db = parser.parse_file(bibfile)
                return bib_db.entries_dict
            except Exception as ex:
                raise forms.ValidationError(
                    _("Error parsing BibTeX: %(msg)s"),
                    params={"msg": str(ex)},
                    code="invalid_bibtex",
                )

    def clean_bibtex_entry(self):
        bibtex = self.cleaned_data.get("bibtex_entry")

        if bibtex is None or bibtex == "":
            return None

        else:
            try:
                parser = BibTexParser(common_strings=True)
                bib_db = parser.parse(bibtex)
                return bib_db.entries_dict
            except Exception as ex:
                raise forms.ValidationError(
                    _("Error parsing BibTeX file: %(msg)s"),
                    params={"msg": str(ex)},
                    code="invalid_bibtex",
                )

    def clean(self):
        cleaned_data = super().clean()
        bibfile = cleaned_data.get("bibtex_file")
        bibentry = cleaned_data.get("bibtex_entry")

        if bibfile is None and bibentry is None:
            raise forms.ValidationError(
                _("These fields cannot both be blank."), code="invalid_bibtex",
            )

        elif bibfile is not None and bibentry is not None:
            raise forms.ValidationError(
                _(
                    "You may upload a .bib file or enter BibTeX manually, but "
                    "not both."
                ),
                code="invalid_bibtex",
            )

        elif bibfile is None and bibentry is not None:
            return {"bibtex": bibentry}

        else:
            return {"bibtex": bibfile}


class NewTagForm(forms.ModelForm):
    """
    NewTagForm allows the creation of new tags. It is a ModelForm based off
    of the CompendiumEntryTag model.
    """

    class Meta:
        model = CompendiumEntryTag
        fields = ("tagname",)

        labels = {"tagname": "Tag name"}

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
