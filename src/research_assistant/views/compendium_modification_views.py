"""
Views related to adding, modifying, or deleting entries from the compendium.
"""

import json

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
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
def research_new_article(request):
    """
    Add a new compendium entry to the site. This view presents users with the
    following forms for creating new compendium entries:
    - A form that manually takes each of the fields of a compendium entry to
      build a new compendium entry.
    - A form that parses a .bib BibTeX file or a raw BibTeX string to
      automatically generate new entries.
    """
    new_entry_form = CompendiumEntryForm(
        request.POST if request.POST and "edit-entry" in request.POST else None
    )
    bibtex_form = BibTexUploadForm(
        request.POST if request.POST and "bibtex-upload" in request.POST else None,
        request.FILES if request.POST and "bibtex-upload" in request.POST else None,
    )
    context = {
        "bibtex_form": bibtex_form,
        "new_entry_form": new_entry_form,
    }

    if request.POST:
        # User edited entry manually
        if "edit-entry" in request.POST and new_entry_form.is_valid():
            context["manual_entry_active"] = True
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

            return redirect("research dashboard")

        elif "bibtex-upload" in request.POST and bibtex_form.is_valid():
            context["bibtex_upload_active"] = True
            bibtex = bibtex_form.cleaned_data.get("bibtex")

            # Add a new entry to the compendium for each entry in the .bib file
            for entry in bibtex.values():
                fields = {
                    "title": entry.get("title"),
                    "url": entry.get("url"),
                    "abstract": entry.get("abstract"),
                    "year": int(entry["year"]) if "year" in entry else None,
                }
                CompendiumEntry.objects.create(**fields)

            return redirect("research dashboard")

    return render(request, "new_article.html", context=context)


@login_required
@require_http_methods(["GET", "POST"])
def research_add_tag(request):
    """
    A view presenting a form to the user that allows them to add a new tag
    to the site.
    """
    form = NewTagForm(request.POST if request.POST else None)
    success = None

    if request.POST and form.is_valid():
        tag = form.save()
        success = True

    tags = CompendiumEntryTag.objects.all()
    return render(
        request,
        "new_tag.html",
        context={"form": form, "existing_tags": tags, "success": success},
    )


@login_required
@require_http_methods(["GET", "POST"])
def research_edit_entries(request, **kwargs):
    """
    A view that allows users to edit entries that they've added to the site.
    """

    get_id = kwargs.get("id", None)
    # allow only authorized user to edit
    if get_id and CompendiumEntry.objects.get(id=get_id).owner == request.user:
        entry = CompendiumEntry.objects.get(id=get_id)

        authors = []
        for author in entry.authors.all():
            authors.append(author.authorname)

        form = CompendiumEntryForm(instance=entry)
        if request.POST:
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
        return render(
            request,
            "new_article.html",
            context={
                "form": form,
                "edit": True,
                "authors": json.dumps(authors),
                "num_of_authors": len(authors),
            },
        )
    else:
        return redirect("list my entries")
