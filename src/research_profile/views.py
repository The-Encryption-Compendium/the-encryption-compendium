from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from research_assistant.models import CompendiumEntry, CompendiumEntryTag
from research_assistant.models import User


@login_required
@require_http_methods(["GET"])
def researcher_profile(request):
    context = {"info": {}, "entries": []}
    my_entries = CompendiumEntry.objects.filter(owner=request.user.id)
    context["info"]["username"] = (
        User.objects.values("username")
        .filter(username=request.user)
        .first()["username"]
    )
    context["info"]["email"] = (
        User.objects.values("email").filter(username=request.user).first()["email"]
    )
    context["info"]["number_of_entries"] = my_entries.count()
    for entry in my_entries:
        entry_dict = {"id": entry.id, "url": entry.url, "title": entry.title}
        tags_query_set = entry.tags.all()
        tags = []
        for tag in tags_query_set:
            tags.append(tag.tagname)
        entry_dict["tags"] = ", ".join(tags)
        context["entries"].append(entry_dict)
    return render(request, "research_profile.html", context)
