"""
Forms for site administration.
"""

from django import forms
from users.models import User


class UserAdminForm(forms.ModelForm):
    """
    A ModelForm based off the custom User model. The UserAdminForm allows
    site admins to manually add new users to the site through Django's admin
    page.
    """

    # A second password field that allow us to double-check any passwords we
    # enter before saving them in the database.
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
