from django import forms
from django.conf import settings
from django.contrib.auth import authenticate, login
from django.contrib.auth.password_validation import validate_password
from django.utils.translation import gettext as _

from research_assistant.models import User

"""
---------------------------------------------------
Login form for researchers
---------------------------------------------------
"""


class ResearchLoginForm(forms.Form):
    """
    Form fields
    """

    username = forms.CharField(
        widget=forms.TextInput(attrs={"placeholder": "Username"}),
        help_text="Enter the username you registered with",
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"placeholder": "Password"}),
        help_text="Enter your password",
    )

    """
    Form validation
    """

    def clean(self):
        cleaned_data = super().clean()

        username = cleaned_data.get("username")
        password = cleaned_data.get("password")

        if not User.objects.filter(username=username).exists():
            raise forms.ValidationError(
                _(f"User '%(username)s' does not exist."),
                params={"username": username},
                code="nonexistent",
            )

        user = User.objects.get(username=username)
        if not user.is_active:
            raise forms.ValidationError(
                _("This user's account is currently disabled."), code="inactive_account"
            )

        user = authenticate(username=username, password=password)
        if not user:
            raise forms.ValidationError(
                _("Sorry, that login was invalid. Please try again."),
                code="invalid_login",
            )

        return cleaned_data

    def login(self, request):
        username = self.cleaned_data.get("username")
        password = self.cleaned_data.get("password")

        user = authenticate(username=username, password=password)
        return user
