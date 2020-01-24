from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods

from research_assistant.forms import ResearchLoginForm

# Create your views here.


"""
---------------------------------------------------
Login view
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


"""
---------------------------------------------------
Researcher interface
---------------------------------------------------
"""


@login_required
@require_http_methods(["GET"])
def research_dashboard(request):
    return render(request, "dashboard.html")