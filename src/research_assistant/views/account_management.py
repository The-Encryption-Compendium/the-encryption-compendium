from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from django.contrib.auth import authenticate
from entries.models import CompendiumEntry, CompendiumEntryTag
from users.forms import PasswordChangeForm
from users.models import User


@login_required
@require_http_methods(["GET", "POST"])
def research_settings(request):
    """
    Provides a view with which users can modify their settings
    """
    passchange_form = PasswordChangeForm(request.POST if request.POST else None)
    if request.method == "POST":
        if passchange_form.is_valid():
            newpassword = passchange_form.cleaned_data["newpassword1"]
            username = request.user.username
            password = passchange_form.cleaned_data["oldpassword"]

            user = authenticate(username=username, password=password)

            if user:
                user.set_password(newpassword)
                user.save()
                return redirect("research dashboard")

            else:
                return render(
                    request,
                    "change_password.html",
                    {
                        "form_errors": "You have entered wrong old password",
                        "form": passchange_form,
                    },
                )

    else:
        form = PasswordChangeForm()

    return render(
        request, "research_settings.html", {"passchange_form": passchange_form}
    )


@login_required
@require_http_methods(["GET"])
def researcher_profile(request):
    """
    Display the user's profile information to them.
    """
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
