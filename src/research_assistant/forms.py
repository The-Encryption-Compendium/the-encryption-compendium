"""
Custom forms for the research assistant app, when forms defined in other
apps won't work.
"""

import bibtexparser
import json
import re

from bibtexparser.bparser import BibTexParser
from django import forms
from django.utils.translation import gettext as _
from entries.forms import CompendiumEntryForm
from utils.dates import month_num


class JsonUploadForm(forms.Form):
    """
    Form for exporting data from Zotero in JSON format and then uploading
    it to the site.
    """

    json_file = forms.FileField(required=True, max_length=5e6,)  # 5 Mb

    """
    Helper functions
    """

    def _read_json_file(self, json_file):
        try:
            return json.load(json_file)
        except Exception as ex:
            raise forms.ValidationError(
                _("Unable to parse JSON file."), code="invalid_json",
            )

    def _extract_date(self, item):
        if "issued" in item:
            date = item["issued"]["date-parts"][0]
        else:
            date = []

        while len(date) < 3:
            date.append(None)

        return date

    def _extract_authors(self, item):
        authors = []
        if "author" in item:
            for author in item["author"]:
                given = author.get("given", "")
                family = author.get("family", "")
                if given != "" and family != "":
                    authors.append(f"{given} {family}")
                elif given == "" and family != "":
                    authors.append(family)
                elif given != "" and family == "":
                    authors.append(given)

        return authors

    """
    Form validation
    """

    def clean_json_file(self):
        json_file = self.cleaned_data.get("json_file")
        data = self._read_json_file(json_file)

        # Extract individual fields out of the file
        entries = []
        for item in data.get("items", []):
            title = item.get("title")
            abstract = item.get("abstract", None)
            new_entry = {
                "title": item.get("title"),
                "abstract": item.get("abstract"),
                "url": item.get("URL"),
            }

            # Convert date
            year, month, day = self._extract_date(item)
            new_entry["year"] = year
            new_entry["month"] = month
            new_entry["day"] = day

            # Get all of the entry's authors
            # new_entry["authors"] = self._extract_authors(item)

            entries.append(new_entry)

        return entries

    def clean(self):
        """
        Pass cleaned data from multiple CompendiumEntryForms.
        """

        cleaned_data = super().clean()
        new_entry_forms = []

        # Loop over every entry we're creating and ensure that it's valid
        for entry in cleaned_data["json_file"]:
            # TODO: add more descriptive error messages in the case where
            # we're invalid.
            new_entry_form = CompendiumEntryForm(data=entry)
            if not new_entry_form.is_valid():
                raise forms.ValidationError(
                    _("There was an error validating the form: %(err)s"),
                    params={"err": repr(new_entry_form.errors)},
                    code="compendium_entry_form_error",
                )
            else:
                new_entry_forms.append(new_entry_form)

        return new_entry_forms


class BibTexUploadForm(forms.Form):
    """
    BibTexUploadForm is an input form that allows adding new compendium entries
    to the site by uploading a .bib file.

    Fields
    ------
    bibtex_file : forms.FileField
        A form field that accepts a .bib file and parses BibTeX from that file.
    """

    # Form field that can be used to upload a .bib file
    bibtex_file = forms.FileField(required=True, max_length=5e6,)  # 5 Mb

    """
    Helper functions
    """

    def _read_bibtex_file(self, bibtex_file) -> dict:
        parser = BibTexParser(common_strings=True)

        try:
            bib_db = parser.parse_file(bibtex_file)
        except Exception as ex:
            raise forms.ValidationError(
                _("Error parsing BibTeX: %(msg)s"),
                params={"msg": str(ex)},
                code="invalid_bibtex",
            )

        return bib_db.entries_dict

    """
    Function for reading Zotero's BibTeX output
    """

    def _extract_date(self, entry):
        # TODO: day
        year = entry.get("year")
        month = entry.get("month")
        if year is not None:
            year = int(year)
        if month is not None:
            month = month_num(month)
        return year, month, None

    def _extract_title(self, entry):
        title = entry.get("title")
        if title is not None:
            # Strip brackets { } from the title
            title = title.replace("{", "").replace("}", "")
        return title

    def _extract_publisher(self, entry):
        for key in ("publisher", "journal", "journaltitle"):
            if key in entry:
                return key[entry]
        return None

    def _extract_tags(self, entry):
        tags = entry.get("keywords")
        if tags is not None:
            tags = tags.split(", ")
        else:
            tags = []
        return tags

    def _extract_authors(self, entry):
        authors = entry.get("author")
        if authors is not None:
            patt = re.compile(r"\{([^\}]+)\}")
            authors = patt.findall(authors)
        else:
            authors = []
        return authors

    def reformat_bibtex(self, bibtex: dict):
        """
        Reformat the BibTeX received by the form into a format that's more easily
        digestible by other parts of the code.
        """

        entries = []

        for entry in bibtex.values():
            year, month, day = self._extract_date(entry)
            entries.append(
                {
                    "entry": {
                        "title": self._extract_title(entry),
                        "publisher_text": self._extract_publisher(entry),
                        "year": year,
                        "month": month,
                        "day": day,
                        "url": entry.get("url"),
                    },
                    "authors": self._extract_authors(entry),
                    "tags": self._extract_tags(entry),
                }
            )

        return entries

    """
    Validation functions
    """

    def clean_bibtex_file(self):
        bibfile = self.cleaned_data.get("bibtex_file")
        bib_dict = self._read_bibtex_file(bibfile)
        entries = self.reformat_bibtex(bib_dict)

        return entries

    def clean(self):
        cleaned_data = super().clean()
        entries = cleaned_data.get("bibtex_file", [])

        # Loop over every entry we're creating and use CompendiumEntryForm
        # to ensure that it's valid.
        new_entry_forms = []
        for entry in entries:
            entry_data = entry.pop("entry")
            form = CompendiumEntryForm(data=entry_data)
            if not form.is_valid():
                # TODO: improved error message
                raise forms.ValidationError(
                    _("There was an error validating the form: %(err)s"),
                    params={"err": repr(form.errors)},
                    code="compendium_entry_form_error",
                )
            else:
                new_entry_forms.append(
                    {**entry, "form": form,}
                )

        return new_entry_forms
