from django import forms
from django.conf import settings
from django.contrib.auth.password_validation import validate_password
from research_assistant.models import User


class PasswordChangeForm(forms.Form):

    oldpassword = forms.CharField(
        widget=forms.PasswordInput(attrs={"placeholder": "Your old Password"}),
        help_text="Enter your old password",
    )
    newpassword1 = forms.CharField(
        widget=forms.PasswordInput(attrs={"placeholder": "New Password"}),
        help_text="Enter a new password",
    )
    newpassword2 = forms.CharField(
        widget=forms.PasswordInput(attrs={"placeholder": "Confirm New Password"}),
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
