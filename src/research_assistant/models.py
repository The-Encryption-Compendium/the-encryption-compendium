from django.conf import settings
from django.contrib import admin
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.conf import settings
from django.db import models
from django.utils import timezone
from django.urls import reverse

from research_assistant.managers import UserManager

from uuid import uuid4

"""
---------------------------------------------------
Model settings
---------------------------------------------------
"""

"""User model"""
MAX_EMAIL_ADDRESS_LENGTH = 100
MAX_USERNAME_LENGTH = 20

MAX_PASSWORD_LENGTH = settings.MAX_PASSWORD_LENGTH
MIN_PASSWORD_LENGTH = settings.MIN_PASSWORD_LENGTH

"""CompendiumEntry model"""
MAX_TITLE_LENGTH = 150
MAX_ABSTRACT_LENGTH = 5000
MAX_URL_LENGTH = 100

"""CompendiumEntryTag model"""
MAX_TAG_LENGTH = 30

"""
---------------------------------------------------
Custom user model
---------------------------------------------------
"""


class User(AbstractBaseUser, PermissionsMixin):
    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]

    ### User fields
    username = models.CharField(
        max_length=MAX_USERNAME_LENGTH, unique=True, blank=False
    )
    email = models.EmailField(
        max_length=MAX_EMAIL_ADDRESS_LENGTH, unique=True, blank=False
    )

    date_joined = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)

    ### Permissions
    is_staff = models.BooleanField(default=False)

    ### Manager object
    # UserManager is used to create new users and superusers. It validates all
    # of the user's fields before creating the user
    objects = UserManager()


"""
---------------------------------------------------
Tags for entries in the compendium
---------------------------------------------------
"""


class CompendiumEntryTag(models.Model):
    tagname = models.CharField(
        max_length=MAX_TAG_LENGTH, blank=False, null=False, unique=True
    )


"""
---------------------------------------------------
Model to represent articles/research/etc that's been added to
the database.
---------------------------------------------------
"""


class CompendiumEntry(models.Model):
    title = models.CharField(max_length=MAX_TITLE_LENGTH, blank=False)
    abstract = models.CharField(max_length=MAX_ABSTRACT_LENGTH, blank=True, null=True)
    url = models.URLField(max_length=MAX_URL_LENGTH, blank=True, null=True)

    tags = models.ManyToManyField(CompendiumEntryTag, blank=True)

    date_added = models.DateTimeField(default=timezone.now)
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)


"""
---------------------------------------------------
Tokens that are sent out when verifying a new user's email.
---------------------------------------------------
"""


class EmailVerificationToken(models.Model):
    email = models.EmailField(
        max_length=MAX_EMAIL_ADDRESS_LENGTH, blank=False, null=False, unique=True
    )
    token = models.UUIDField(default=uuid4, unique=True)

    @property
    def email_verification_location(self):
        return f"{reverse('add new user')}?token={self.token}"
