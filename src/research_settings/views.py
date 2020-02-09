from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from django.contrib.auth import authenticate
from research_settings.forms import PasswordChangeForm


@login_required
@require_http_methods(["GET"])
def research_settings(request):
    return render(request, "research_settings.html")


@login_required
@require_http_methods(["GET", "POST"])
def change_password(request):

    if request.method == "POST":
        form = PasswordChangeForm(request.POST)
        if form.is_valid():
            newpassword = form.cleaned_data["newpassword1"]
            username = request.user.username
            password = form.cleaned_data["oldpassword"]

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
                        "form": form,
                    },
                )

    else:
        form = PasswordChangeForm()
    return render(request, "change_password.html", {"form": form})
