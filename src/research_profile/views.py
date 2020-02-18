from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from research_assistant.models import CompendiumEntry, CompendiumEntryTag


@login_required
@require_http_methods(["GET"])
def research_profile(request):
    return render(request, "research_profile.html")


@login_required
@require_http_methods(["GET"])
def research_my_entries(request):
    my_entries = CompendiumEntry.objects.filter(owner=request.user.id)
    context = {"entries": []}
    for entry in my_entries:
        entry_dict = {"id": entry.id, "url": entry.url, "title": entry.title}
        tags_query_set = entry.tags.all()
        tags = []
        for tag in tags_query_set:
            tags.append(tag.tagname)
        entry_dict["tags"] = ", ".join(tags)
        context["entries"].append(entry_dict)
    return render(request, "research_my_entries.html", context=context)
