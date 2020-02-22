from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from django.contrib.auth import authenticate
from research_settings.forms import PasswordChangeForm


@login_required
@require_http_methods(["GET", "POST"])
def research_settings(request):
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
