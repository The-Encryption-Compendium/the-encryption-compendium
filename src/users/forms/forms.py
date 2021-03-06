"""
Code for forms related to authentication and signup
"""

from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.utils.translation import gettext as _
from users.models import User, SignupToken, MAX_EMAIL_ADDRESS_LENGTH
from utils.widgets import EmailTextInput


class ResearchLoginForm(forms.Form):
    """
    Generic login form for users to the site.
    """

    username = forms.CharField(
        widget=forms.TextInput(
            attrs={"class": "uk-input uk-width-1-1", "placeholder": "Username"}
        ),
        help_text="Enter the username you registered with",
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"class": "uk-input uk-width-1-1", "placeholder": "Password"}
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


class SignupForm(forms.ModelForm):
    """
    This form is presented to users upon initializing their account. It allows
    them to set options such as their username and password.
    """

    password_2 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "uk-input uk-width-1-1",
                "placeholder": "Enter your password again",
            },
        ),
        help_text="Enter your password again",
        label="",
    )

    class Meta:
        model = User
        fields = ("email", "username", "password", "password_2")
        labels = {
            "email": "Email",
            "username": "Username",
            "password": "Password",
        }

        widgets = {
            "email": EmailTextInput(attrs={"class": "uk-width-1-1"},),
            "username": forms.TextInput(
                attrs={
                    "class": "uk-input uk-width-1-1",
                    "placeholder": "Pick a username",
                },
            ),
            "password": forms.PasswordInput(
                attrs={
                    "class": "uk-input uk-width-1-1",
                    "placeholder": "Choose your password",
                },
            ),
        }

    def clean_password_2(self):
        password = self.cleaned_data.get("password")
        password_2 = self.cleaned_data.get("password_2")

        if password != password_2:
            raise forms.ValidationError(
                _("Passwords must match."), code="nonmatching_passwords"
            )

        return password_2


class AddNewUserForm(forms.ModelForm):
    """
    Form to add a new user to the site. Site admins can use this form to invite
    new users and create accounts for them.
    """

    class Meta:
        model = SignupToken
        fields = ("email",)
        labels = {"email": "New user email"}
        help_texts = {"email": "The new user's email address"}
        widgets = {
            "email": EmailTextInput(),
        }

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email")

        # Email cannot already belong to a registered user
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(
                _("This email address has already been registered."),
                params={"email": email},
            )

        return cleaned_data


class TokenDeleteForm(forms.Form):

    email = forms.CharField(max_length=MAX_EMAIL_ADDRESS_LENGTH)

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        if not SignupToken.objects.filter(email=email).exists():
            raise forms.ValidationError(
                _("Token does not exist for %(email)s"),
                params={"email": email},
                code="token_does_not_exist",
            )

        return cleaned_data


class PasswordChangeForm(forms.Form):
    """
    A form for allowing users to change their password. The form requires
    that users enter their old password, and then enter their new password
    twice.
    """

    oldpassword = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Your old Password",
                "class": "uk-input uk-form-width-large",
            }
        ),
        help_text="Enter your old password",
    )
    newpassword1 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "New Password",
                "class": "uk-input uk-form-width-large",
            }
        ),
        help_text="Enter a new password",
    )
    newpassword2 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Confirm New Password",
                "class": "uk-input uk-form-width-large",
            }
        ),
        help_text="Re-enter the password",
    )

    def clean(self):
        cleaned_data = super().clean()

        if "newpassword1" in cleaned_data and "newpassword2" in cleaned_data:
            if self.cleaned_data["newpassword1"] != self.cleaned_data["newpassword2"]:
                raise forms.ValidationError("The two password fields did not match.")

        try:
            validate_password(self.cleaned_data["newpassword1"])
        except forms.ValidationError:
            raise forms.ValidationError("Password did not meet minimum requirements")

        if "oldpassword" in cleaned_data and "newpassword1" in cleaned_data:
            if self.cleaned_data["newpassword1"] == self.cleaned_data["oldpassword"]:
                raise forms.ValidationError(
                    "Old and new passwords need to be different"
                )

        return self.cleaned_data
