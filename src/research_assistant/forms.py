from django import forms
from django.conf import settings
from django.contrib.auth import authenticate, login
from django.contrib.auth.password_validation import validate_password
from django.utils.translation import gettext as _

from research_assistant.models import User, CompendiumEntry

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
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Username"}
        ),
        help_text="Enter the username you registered with",
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Password"}
        ),
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
                _(f"Username does not exist."), code="nonexistent"
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


"""
---------------------------------------------------
Model administration forms
---------------------------------------------------
"""


class UserAdminForm(forms.ModelForm):
    """
    A ModelForm based off the custom User model for manually adding new users
    to the site.
    """

    password_2 = forms.CharField(
        widget=forms.PasswordInput(attrs={"placeholder": "Re-enter password"}),
        label="Enter password again",
    )

    class Meta:
        model = User
        fields = (
            "email",
            "username",
            "password",
            "password_2",
            "is_staff",
            "is_superuser",
        )

        widgets = {
            "email": forms.TextInput(attrs={"placeholder": "Email address"}),
            "username": forms.TextInput(attrs={"placeholder": "Username"}),
            "password": forms.PasswordInput(attrs={"placeholder": "Password"}),
        }

        labels = {
            "is_staff": "Add as a staff member",
            "is_superuser": "Add as superuser",
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_2 = cleaned_data.get("password_2")

        if password != password_2:
            error = forms.ValidationError(
                _("The passwords you've entered don't match. Please try again."),
                code="nonmatching_passwords",
            )
            self.add_error("password_2", error)

        return cleaned_data


class CompendiumEntryForm(forms.ModelForm):
    class Meta:
        model = CompendiumEntry
        fields = (
            "title",
            "abstract",
            "url",
            "owner",  # logged by the server. can be removed from the form
            "tags",
        )

        widgets = {
            "abstract": forms.Textarea(),
            "owner": forms.TextInput(
                attrs={"disabled": True}
            ),  # logged by the server. can be removed from the form
        }

        labels = {"url": "URL"}
