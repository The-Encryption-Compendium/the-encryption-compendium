from django.conf import settings
from django.contrib import admin
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.conf import settings
from django.db import models
from django.utils import timezone
from django.urls import reverse
from datetime import date

from research_assistant.managers import UserManager
from django.core.validators import MaxValueValidator, MinValueValidator

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

"""Authors model"""
MAX_AUTHOR_NAME_LENGTH = 20

"""Publisher model"""
MAX_PUBLISHER_NAME_LENGTH = 20

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

    def __str__(self):
        return str(self.tagname)


"""
-----------------------------------------------------
Model to represent Authors of the article
-----------------------------------------------------
"""


class Author(models.Model):
    authorname = models.CharField(
        max_length=MAX_AUTHOR_NAME_LENGTH, blank=False, null=False, unique=True
    )

    def __str__(self):
        return str(self.authorname)


"""
-----------------------------------------------------
Model to represent Publisher of the article
-----------------------------------------------------
"""


class Publisher(models.Model):
    publishername = models.CharField(
        max_length=MAX_PUBLISHER_NAME_LENGTH, blank=True, null=True
    )

    def __str__(self):
        return str(self.publishername)


"""
---------------------------------------------------
Model to represent articles/research/etc that's been added to
the database.
---------------------------------------------------
"""


class CompendiumEntry(models.Model):
    title = models.CharField(max_length=MAX_TITLE_LENGTH, blank=False, null=False)
    abstract = models.CharField(max_length=MAX_ABSTRACT_LENGTH, blank=True, null=True)
    url = models.URLField(max_length=MAX_URL_LENGTH, blank=True, null=True)

    tags = models.ManyToManyField(CompendiumEntryTag, blank=True)

    date_added = models.DateTimeField(default=timezone.now)
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    publisher_text = models.CharField(
        max_length=MAX_PUBLISHER_NAME_LENGTH, blank=True, null=True
    )
    publisher = models.ForeignKey(
        Publisher, on_delete=models.SET_NULL, blank=True, null=True
    )
    """ Three int fields to add published date """
    year = models.PositiveSmallIntegerField(
        validators=[MaxValueValidator(date.today().year), MinValueValidator(1900)],
        blank=True,
        null=True,
    )
    month = models.PositiveSmallIntegerField(
        validators=[MaxValueValidator(12), MinValueValidator(1)], blank=True, null=True
    )
    day = models.PositiveSmallIntegerField(
        validators=[MaxValueValidator(31), MinValueValidator(1)], blank=True, null=True
    )


"""
---------------------------------------------------
Tokens that are sent out when verifying a new user's email.
---------------------------------------------------
"""


class SignupToken(models.Model):
    email = models.EmailField(
        max_length=MAX_EMAIL_ADDRESS_LENGTH, blank=False, null=False, unique=True
    )
    token = models.UUIDField(default=uuid4, unique=True)

    @property
    def signup_location(self):
        return f"{reverse('sign up')}?token={self.token}"
