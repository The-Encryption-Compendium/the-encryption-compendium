"""
Models directly related to users and user authentication.
"""

from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.urls import reverse
from django.utils import timezone
from research_assistant.managers import UserManager
from uuid import uuid4

"""
---------------------------------------------------
Configuration variables
---------------------------------------------------
"""

MAX_EMAIL_ADDRESS_LENGTH = 100
MAX_USERNAME_LENGTH = 20

MAX_PASSWORD_LENGTH = settings.MAX_PASSWORD_LENGTH
MIN_PASSWORD_LENGTH = settings.MIN_PASSWORD_LENGTH

"""
---------------------------------------------------
Models
---------------------------------------------------
"""


class User(AbstractBaseUser, PermissionsMixin):
    """
    A custom user model for the site.

    Fields
    ------
    username : django.db.models.CharField
        The user's username. This is the field they use to authenticate to
        the site.

    email : django.db.models.EmailField
        The user's email address.

    date_joined : django.db.models.DateTimeField
        The date on which the user joined the site. Defaults to the time at
        which create_user() is called.

    is_active : django.db.models.BooleanField
        Whether or not the user's account has been locked.

    is_staff : django.db.models.BooleanField
        Whether or not the user is a staff member for the site. Staff members
        have higher administrative abilities than regular users. Being a staff
        member does not imply being a superuser, which provides a higher level
        of permissions.
    """

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


class SignupToken(models.Model):
    """
    A signup token that allows a new user to sign up to the site. In practice,
    a SignupToken is sent to a person's email address when we want them to
    sign up for the site. The token is consumed when the new user has successfully
    signed up.

    Fields
    ------
    email : django.db.models.EmailField
        The email address of the person that we would like to invite to be a
        user on the site.

    token : django.db.models.UUIDField
        A randomized UUID that uniquely identifies the token. The UUID is
        emailed to the newly invited user in the form of a link which allows
        them to sign up for the site.
    """

    email = models.EmailField(
        max_length=MAX_EMAIL_ADDRESS_LENGTH, blank=False, null=False, unique=True
    )
    token = models.UUIDField(default=uuid4, unique=True)

    @property
    def signup_location(self):
        return f"{reverse('sign up')}?token={self.token}"
