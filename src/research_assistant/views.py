from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.conf import settings
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from research_assistant.forms import (
    AddNewUserForm,
    CompendiumEntryForm,
    NewTagForm,
    ResearchLoginForm,
)
from research_assistant.models import CompendiumEntryTag, EmailVerificationToken

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
    form = AddNewUserForm(request.POST if request.POST else None)
    if request.POST and form.is_valid():
        token = form.save()
        url = request.build_absolute_uri(token.email_verification_location)
        send_mail(
            "You have been invited to create researcher account for The Encryption Compendium.",
            f"Use this link to sign up:\n\n{url}",
            settings.EMAIL_HOST_USER,
            [form["email"]],
        )

    return render(request, "add_user.html", context={"form": form})


"""
---------------------------------------------------
Researcher interface
---------------------------------------------------
"""


@login_required
@require_http_methods(["GET"])
def research_dashboard(request):
    return render(request, "dashboard.html")


@login_required
@require_http_methods(["GET", "POST"])
def research_new_article(request):
    form = CompendiumEntryForm(request.POST if request.POST else None)
    if request.POST and form.is_valid():
        article = form.save()
        article.user = request.user
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
