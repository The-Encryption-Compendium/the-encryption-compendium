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


class JsonUploadForm(forms.Form):
    """
    Form for exporting data from Zotero in JSON format and then uploading
    it to the site.
    """

    json_file = forms.FileField(required=False, max_length=5e6,)  # 5 Mb

    """
    Helper functions
    """

    def _read_json_file(self, json_file):
        try:
            return json.load(json_file)
        except Exception as ex:
            print("EXCEPTION:", ex)
            raise forms.ValidationError(
                _("Unable to parse JSON file."), code="invalid_json",
            )

    def _extract_date(self, item):
        if "issued" in item:
            year, month, day = item["issued"]["date-parts"][0]
            return year, month, day
        else:
            return None, None, None

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
            new_entry["authors"] = self._extract_authors(item)

            entries.append(new_entry)

        return entries


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
                "class": "monospace uk-width-1-1 uk-textarea",
                "placeholder": "Copy BibTex here...",
            }
        ),
        required=False,
    )

    """
    Helper functions
    """

    def reformat_bibtex(self, bibtex: dict):
        """
        Reformat the BibTeX received by the form into a format that's more easily
        digestible by other parts of the code.
        """

        for entry in bibtex.values():
            authors = entry.get("author")
            if authors is not None:
                # Strip brackets { } from the author string
                patt = re.compile(r"\{([^\}]+)\}")
                names = patt.findall(authors)
                entry["author"] = names

            title = entry.get("title")
            if title is not None:
                # Strip brackets { } from the title
                entry["title"] = title.replace("{", "").replace("}", "")

        return bibtex

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
            return {"bibtex": self.reformat_bibtex(bibentry)}

        else:
            return {"bibtex": self.reformat_bibtex(bibfile)}
