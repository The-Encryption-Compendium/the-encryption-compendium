from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.conf import settings
from django.db import models
from django.utils import timezone

# from .auth import EmailBackend
from .managers import UserManager

"""
---------------------------------------------------
User model settings
---------------------------------------------------
"""

MAX_EMAIL_ADDRESS_LENGTH = 100

MAX_PASSWORD_LENGTH = settings.MAX_PASSWORD_LENGTH
MIN_PASSWORD_LENGTH = settings.MIN_PASSWORD_LENGTH

"""
---------------------------------------------------
Custom user model
---------------------------------------------------
"""


class User(AbstractBaseUser, PermissionsMixin):
    # Use email address in place of a username when logging in
    USERNAME_FIELD = "email"

    ### User fields
    email = models.EmailField(
        max_length=MAX_EMAIL_ADDRESS_LENGTH, unique=True, blank=False
    )
    date_joined = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)

    # EmailBackend is an authentication backend that allows users to sign in
    # with their email address.

    # UserManager is used to create new users and superusers. It validates all
    # of the user's fields before creating the user
    objects = UserManager()
