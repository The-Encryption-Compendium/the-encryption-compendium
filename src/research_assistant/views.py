from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.conf import settings
from django.core.mail import send_mail
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from research_assistant.forms import (
    AddNewUserForm,
    CompendiumEntryForm,
    NewTagForm,
    ResearchLoginForm,
    SignupForm,
    TokenDeleteForm,
    EntryDeleteForm,
)
from research_assistant.models import CompendiumEntry, CompendiumEntryTag, SignupToken

# Create your views here.


"""
---------------------------------------------------
Authentication-related views
---------------------------------------------------
"""


@require_http_methods(["GET", "POST"])
def research_login(request):
    if request.user.is_authenticated:
        return redirect("research dashboard")

    # On a POST request, attempt to login
    form = ResearchLoginForm(request.POST if request.POST else None)
    if request.POST and form.is_valid():
        user = form.login(request)
        if user:
            # Login and redirect based on the 'next' URL parameter (if
            # it exists).
            login(request, user)
            redirect_url = request.GET.get("next", "research dashboard")
            return redirect(redirect_url)

    return render(request, "login.html", context={"form": form})


@require_http_methods(["GET"])
def research_logout(request):
    if request.user.is_authenticated:
        logout(request)
    return redirect("research login")


@login_required
@user_passes_test(lambda user: user.is_staff)
@require_http_methods(["GET", "POST"])
def add_new_user(request):
    """
    An admin view that allows staff members to invite new researchers to create an
    account on the site.
    """
    form = AddNewUserForm(request.POST if request.POST else None)
    created_user = False
    if request.POST and "create_user" in request.POST and form.is_valid():
        token = form.save()
        url = request.build_absolute_uri(token.signup_location)
        send_mail(
            "You have been invited to create researcher account for The Encryption Compendium.",
            f"Use this link to sign up:\n\n{url}",
            settings.EMAIL_HOST_USER,
            [form.cleaned_data["email"]],
        )
        created_user = True
    elif request.POST and "del_email" in request.POST:
        delete_form = TokenDeleteForm({"email": request.POST["del_email"]})
        if delete_form.is_valid():
            email = delete_form.cleaned_data["email"]
            SignupToken.objects.get(email=email).delete()

    outstanding_tokens = SignupToken.objects.all()

    return render(
        request,
        "add_user.html",
        context={
            "form": form,
            "outstanding_tokens": outstanding_tokens,
            "created_user": created_user,
        },
    )


@require_http_methods(["GET", "POST"])
def sign_up(request):
    # Request must include a valid authentication token
    token = request.GET.get("token", None)
    valid_token = True
    if token is None:
        valid_token = False
    else:
        # Check that token is valid
        matching_token = SignupToken.objects.filter(token=token)
        if not matching_token.exists():
            valid_token = False
        else:
            matching_token = matching_token[0]

    if not valid_token:
        return HttpResponseForbidden()

    # Display signup form
    form = SignupForm(
        request.POST if request.POST else None, initial={"email": matching_token.email}
    )
    if request.POST and form.is_valid():
        new_user = form.save()
        matching_token.delete()

        # Log the user in and redirect them to the dashboard
        login(request, new_user)
        return redirect("research dashboard")

    return render(request, "sign_up.html", context={"form": form})


"""
---------------------------------------------------
Researcher interface
---------------------------------------------------
"""


@login_required
@require_http_methods(["GET"])
def research_dashboard(request):
    context = {"entries": []}
    all_entries = CompendiumEntry.objects.all()
    for entry in all_entries:
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
    return render(request, "dashboard.html", context=context)


@login_required
@require_http_methods(["GET", "POST"])
def research_new_article(request):
    form = CompendiumEntryForm(request.POST if request.POST else None)
    if request.POST and form.is_valid():
        article = form.save()
        article.owner = request.user
        article.save()
        return redirect("research dashboard")
    return render(request, "new_article.html", context={"form": form})


@login_required
@require_http_methods(["GET", "POST"])
def research_add_tag(request):
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
@require_http_methods(["GET"])
def research_my_entries(request):
    return render(request, "my_entries_options.html")


@login_required
@require_http_methods(["GET", "POST"])
def research_list_my_entries(request):

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


@login_required
@require_http_methods(["GET", "POST"])
def research_edit_entries(request, **kwargs):
    get_id = kwargs.get("id", None)
    # allow only authorized user to edit
    if get_id and CompendiumEntry.objects.get(id=get_id).owner == request.user:
        entry = CompendiumEntry.objects.get(id=get_id)
        form = CompendiumEntryForm(instance=entry)
        if request.POST:
            form = CompendiumEntryForm(request.POST, instance=entry)
            if form.is_valid():
                article = form.save()
                article.save()
                return redirect("research dashboard")
        return render(request, "new_article.html", context={"form": form, "edit": True})
    else:
        return redirect("list my entries")
