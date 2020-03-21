from django.contrib.auth.models import BaseUserManager

"""
---------------------------------------------------
UserManager object for the custom User object
---------------------------------------------------
"""


class UserManager(BaseUserManager):
    def create_user(self, username, email, password, **extra_fields):
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)

        # Validate the User instance's fields, and then save the User to
        # the database.
        result = user.full_clean()

        # TODO: check result?
        user.save()

        return user

    def create_superuser(self, username, email, password, **extra_fields):
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_staff", True)
        return self.create_user(
            username=username, email=email, password=password, **extra_fields
        )
