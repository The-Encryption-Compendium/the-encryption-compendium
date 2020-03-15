"""
Authentication-related views.
"""

from django.conf import settings
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.mail import send_mail
from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from research_assistant.forms import (
    AddNewUserForm,
    ResearchLoginForm,
    SignupForm,
    TokenDeleteForm,
)
from research_assistant.models import SignupToken


@require_http_methods(["GET", "POST"])
def research_login(request):
    """
    Login page for the site.
    """
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
    """
    An endpoint that, when visited, will log a user out of their account.
    """
    if request.user.is_authenticated:
        logout(request)
    return redirect("research login")


@login_required
@user_passes_test(lambda user: user.is_staff)
@require_http_methods(["GET", "POST"])
def add_new_user(request):
    """
    An admin view that allows staff members to invite new researchers to create
    an account on the site.
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
    """
    The page visited by a user when they receive a signup token. The site checks
    that the token is valid before the user is able to continue on to the
    signup page.
    """

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
