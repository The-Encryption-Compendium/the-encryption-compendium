"""
Views related to adding, modifying, or deleting entries from the compendium.
"""

import abc
import json

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect
from django.views import View
from django.views.decorators.http import require_http_methods
from django.views.generic.base import ContextMixin
from django.utils.decorators import method_decorator
from research_assistant.forms import (
    BibTexUploadForm,
    CompendiumEntryForm,
    NewTagForm,
)
from research_assistant.models import (
    CompendiumEntry,
    CompendiumEntryTag,
    Publisher,
    Author,
)


@login_required
@require_http_methods(["GET", "POST"])
def research_add_tag(request):
    """
    A view presenting a form to the user that allows them to add a new tag
    to the site.
    """
    form = NewTagForm(request.POST if request.POST else None)
    tags = CompendiumEntryTag.objects.order_by("tagname").all()

    context = {
        "form": form,
        "tags": tags,
    }

    if request.POST and form.is_valid():
        tag = form.save()
        context["success"] = True

    return render(request, "new_tag.html", context=context,)


"""
---------------------------------------------------
Class-based views for the site
---------------------------------------------------
"""


class AbstractCompendiumEntryModificationView(
    ContextMixin, LoginRequiredMixin, View, metaclass=abc.ABCMeta
):
    """
    A generic view for adding new compendium entries or modifying existing
    compendium entries.

    This class is not actually used directly for any views; rather, it is an
    abstract parent class whose children are actually used for constructing
    new views.
    """

    @abc.abstractmethod
    def get(self, request):
        pass

    @abc.abstractmethod
    def post(self, request):
        pass

    def _edit_entry(self, request):
        """
        Add or modify an entry in the Encryption Compendium using the form for
        manual entry modification.
        """

        new_entry_form = CompendiumEntryForm(request.POST)

        is_valid = new_entry_form.is_valid()
        if is_valid:
            article = new_entry_form.save()

            if not Publisher.objects.filter(
                publishername=article.publisher_text
            ).exists():
                Publisher.objects.create(publishername=article.publisher_text)
            publisher = Publisher.objects.filter(
                publishername=article.publisher_text
            ).first()
            article.publisher = publisher

            authors_list = []
            for author in request.POST.getlist("authors_text"):
                if not Author.objects.filter(authorname=author).exists():
                    Author.objects.create(authorname=author)
                authors_list.append(Author.objects.filter(authorname=author).first())
            article.authors.set(authors_list)

            article.owner = request.user
            article.save()

        return is_valid, new_entry_form

    def _create_entries_from_bibtex(self, request):
        """
        Create one or more new compendium entries using BibTeX that was uploaded
        to the site.
        """

        bibtex_form = BibTexUploadForm(request.POST, request.FILES)

        is_valid = bibtex_form.is_valid()
        if bibtex_form.is_valid():
            bibtex = bibtex_form.cleaned_data.get("bibtex")

            # Add a new entry to the compendium for each entry in the .bib file
            for entry in bibtex.values():
                fields = {
                    "title": entry.get("title"),
                    "url": entry.get("url"),
                    "abstract": entry.get("abstract"),
                    "year": int(entry["year"]) if "year" in entry else None,
                }
                compendium_entry = CompendiumEntry.objects.create(**fields)

                # Get all of the authors of the compendium entry. Due to some weirdness
                # with how Zotero formats BibTeX outputs, we have to perform this regular
                # expression in order to extract the authors.
                names = entry.get("author", [])

                # Set the authors of the compendium entry
                authors_list = []
                for name in names:
                    author = Author.objects.filter(authorname=name)
                    if not author.exists():
                        author = Author.objects.create(authorname=name)
                    else:
                        author = author.first()

                    authors_list.append(author)

                compendium_entry.authors.set(authors_list)
                compendium_entry.owner = request.user
                compendium_entry.save()

        return is_valid, bibtex_form


class NewCompendiumEntryView(AbstractCompendiumEntryModificationView):
    """
    A view for creating new compendium entries on the site. This view presents
    two forms to users:
    - A form that allows users to create new compendium entries by hand.
    - A form for creating compendium entries en masse using BibTeX.
    """

    def get(self, request):
        new_entry_form = CompendiumEntryForm()
        bibtex_form = BibTexUploadForm()
        return render(
            request,
            "new_article.html",
            context={"new_entry_form": new_entry_form, "bibtex_form": bibtex_form,},
        )

    def post(self, request):
        context = {}
        is_valid = False

        if "edit-entry" in request.POST:
            # User edited entry manually
            is_valid, new_entry_form = self._edit_entry(request)
            context["manual_entry_active"] = True
        else:
            new_entry_form = CompendiumEntryForm()

        if "bibtex-upload" in request.POST:
            # User uploaded BibTeX to the site
            is_valid, bibtex_form = self._create_entries_from_bibtex(request)
            context["bibtex_upload_active"] = True
        else:
            bibtex_form = BibTexUploadForm()

        if is_valid:
            return redirect("research dashboard")

        context["new_entry_form"] = new_entry_form
        context["bibtex_form"] = bibtex_form
        return render(
            request,
            "new_article.html",
            context={"new_entry_form": new_entry_form, "bibtex_form": bibtex_form,},
        )


class EditCompendiumEntryView(AbstractCompendiumEntryModificationView):
    """
    This class provides a view for editing entries in the compendium.
    """

    def get(self, request, **kwargs):
        get_id = kwargs.get("id", None)

        # Only authorized users are allowed to edit the entry
        if get_id and CompendiumEntry.objects.get(id=get_id).owner == request.user:
            entry = CompendiumEntry.objects.get(id=get_id)

            authors = []
            for author in entry.authors.all():
                authors.append(author.authorname)

            form = CompendiumEntryForm(instance=entry)
            return render(
                request,
                "new_article.html",
                context={
                    "form": form,
                    "authors": json.dumps(authors),
                    "num_of_authors": len(authors),
                },
            )

        else:
            return HttpResponseForbidden()

    def post(self, request, **kwargs):
        get_id = kwargs.get("id", None)

        # Only authorized users are allowed to edit the entry
        if get_id and CompendiumEntry.objects.get(id=get_id).owner == request.user:
            entry = CompendiumEntry.objects.get(id=get_id)

            authors = []
            for author in entry.authors.all():
                authors.append(author.authorname)

            form = CompendiumEntryForm(request.POST, instance=entry)

            if form.is_valid():
                article = form.save()

                if not Publisher.objects.filter(
                    publishername=article.publisher_text
                ).exists():
                    Publisher.objects.create(publishername=article.publisher_text)
                publisher = Publisher.objects.filter(
                    publishername=article.publisher_text
                ).first()
                article.publisher = publisher

                authors_list = []
                for author in request.POST.getlist("authors_text"):
                    if not Author.objects.filter(authorname=author).exists():
                        Author.objects.create(authorname=author)
                    authors_list.append(
                        Author.objects.filter(authorname=author).first()
                    )
                article.authors.set(authors_list)

                article.save()
                return redirect("research dashboard")

            else:
                return render(
                    request,
                    "new_article.html",
                    context={
                        "form": form,
                        "authors": json.dumps(authors),
                        "num_of_authors": len(authors),
                    },
                )

        else:
            return HttpResponseForbidden()
