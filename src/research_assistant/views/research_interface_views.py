"""
Views related to each researcher's homepage and interface to the site. These
views present customized content to researchers, such as their settings page,
lists of entries that they've added, and so on.
"""

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from research_assistant.forms import EntryDeleteForm
from entries.models import CompendiumEntry


@login_required
@require_http_methods(["GET"])
def research_dashboard(request):
    """
    View for the user's homepage.
    """
    owned_entries = CompendiumEntry.objects.filter(owner=request.user)
    context = {"entries": owned_entries}
    return render(request, "dashboard.html", context=context)


@login_required
@require_http_methods(["GET"])
def research_my_entries(request):
    """
    A page that presents different options for users w.r.t. creating, editing,
    and deleting compendium entries.
    """
    return render(request, "my_entries_options.html")


@login_required
@require_http_methods(["GET", "POST"])
def research_list_my_entries(request):
    """
    A view that lists all of the entries created by a user.
    """
    form = EntryDeleteForm(request.POST if request.POST else None)

    if request.POST and form.is_valid():
        entry_id = form.cleaned_data["entry_id"]
        # allowing only authorized user to delete
        if CompendiumEntry.objects.get(id=entry_id).owner == request.user:
            CompendiumEntry.objects.get(id=entry_id).delete()

    context = {"entries": []}
    my_entries = CompendiumEntry.objects.filter(owner=request.user.id)

    for entry in my_entries:
        entry_dict = {
            "id": entry.id,
            "url": entry.url,
            "title": entry.title,
            "owner": entry.owner,
        }
        tags_query_set = entry.tags.all()
        tags = []

        for tag in tags_query_set:
            tags.append(tag.tagname)
        entry_dict["tags"] = ", ".join(tags)
        context["entries"].append(entry_dict)

    return render(request, "list_my_entries.html", context=context)
