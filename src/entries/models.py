"""
Models related to the site's compendium entries.
"""

from datetime import date
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone
from users.models import User
from utils.dates import month_name
from utils.widgets import MonthWidget
from django.db.models.signals import pre_save
from utils.articles_slug import unique_slug_generator

"""
---------------------------------------------------
Configuration options
---------------------------------------------------
"""

"""CompendiumEntry model"""
MAX_TITLE_LENGTH = 300
MAX_ABSTRACT_LENGTH = 10000
MAX_URL_LENGTH = 300

"""CompendiumEntryTag model"""
MAX_TAG_LENGTH = 30

"""Authors model"""
MAX_AUTHOR_NAME_LENGTH = 100

"""Publisher model"""
MAX_PUBLISHER_NAME_LENGTH = 100

"""
---------------------------------------------------
Models
---------------------------------------------------
"""


class CompendiumEntryTag(models.Model):
    """
    Defines a single tag for a compendium entry. Tags are used as a
    ManyToManyField in the compendium entry model.

    Fields
    ------
    tagname : django.db.models.CharField
        A unique name that is associated with the tag.
    """

    tagname = models.CharField(
        max_length=MAX_TAG_LENGTH, blank=False, null=False, unique=True
    )

    def __str__(self):
        return str(self.tagname)


class Author(models.Model):
    """
    Defines an author of a compendium entry. Authors are used as a ManyToManyField
    in the compendium entry model.

    Fields
    ------
    authorname : django.db.models.CharField
        The name of the author. Defined to be unique. Note that authors' names
        may not necessarily be unique, however, in the absence of other
        identifying information for an author the name alone should usually be
        sufficient.
    """

    authorname = models.CharField(
        max_length=MAX_AUTHOR_NAME_LENGTH, blank=False, null=False, unique=True
    )

    def __str__(self):
        return str(self.authorname)


class Publisher(models.Model):
    """
    The conference, journal, organization, etc. that published a compendium
    entry. Publishers have a one-to-many relationship with compendium entries.
    I.e., a publisher may publish multiple compendium entries, but an entry
    can only be associated with one publisher.

    Fields
    ------
    publishername : django.db.models.CharField
        The name of the publisher. Defined to be unique.
    """

    publishername = models.CharField(
        max_length=MAX_PUBLISHER_NAME_LENGTH, blank=True, null=True, unique=True,
    )

    def __str__(self):
        return str(self.publishername)


class CompendiumEntry(models.Model):
    """
    CompendiumEntry is the primary model used by the project to represent entries
    in the compendium. Articles, papers, official statements, etc. that are
    uploaded by researchers to the site are stored in the database as
    CompendiumEntries.

    Fields
    ------
    title : django.db.models.CharField
        The title of the compendium entry. This is a required field.

    abstract : django.db.models.CharField
        The abstract for the entry. Provides a short description of what the entry
        is related to.

    url : django.db.models.URLField
        A URL for the compendium entry, if one exists. The URL can be used to link
        to an external resource that site visitors can use to learn more about
        the compendium entry.

    tags : django.db.models.ManyToManyField
        The CompendiumEntryTags that are associated with the compendium entry.
        Compendium entries share a many-to-many relationship with tags.

    date_added : django.db.models.DateTimeField
        The date and time at which the compendium entry was added to the site.
        Defaults to the time at which the CompendiumEntry was created.

    owner : django.db.models.ForeignKey
        The site user who created the entry. The compendium entry's owner is
        allowed to edit and delete the entry. Other users need higher permissions
        in order to make edits to the entry.

    publisher_text : django.db.models.CharField

    publisher : django.db.models.ForeignKey
        The conference, journal, organization, etc. that published the compendium
        entry. Publishers share a many-to-one relationship with compendium
        entries.

    authors : django.db.models.ManyToManyField
        The author(s) of the compendium entry. This field is allowed to be blank,
        indicating that the author is unknown.

    year : django.db.models.PositiveSmallIntegerField
        The year in which the compendium entry was published. Note that the
        day, month, and year are represented as separate fields as there may
        be cases in which one of this is unknown.

    month : django.db.models.PositiveSmallIntegerField
        An integer in the range of 1 to 12 that represents the month in which a
        compendium entry was published.

    day : django.db.models.PositiveSmallIntegerField
        An integer representing the day of the month in which a compendium entry
        was published.
    """

    title = models.CharField(max_length=MAX_TITLE_LENGTH, blank=False, null=False)
    slug = models.SlugField(max_length=250, blank=True, null=True)
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

    # authors: all of the authors associated with the entry
    # authors_cs: a comma-separated string of all of the authors.
    authors = models.ManyToManyField(Author, blank=True)
    authors_cs = models.CharField(max_length=1000, blank=True, null=True)

    # Separate year, month, and day fields to specify when the compendium entry
    # was published.
    #
    # The date is represented as three different fields because there may be
    # cases in which e.g. the year of publication is known, but noth the month or
    # day.
    year = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1900)], blank=True, null=True,
    )
    month = models.PositiveSmallIntegerField(
        validators=[MaxValueValidator(12), MinValueValidator(1)], blank=True, null=True
    )
    day = models.PositiveSmallIntegerField(
        validators=[MaxValueValidator(31), MinValueValidator(1)], blank=True, null=True
    )

    """
    Class properties for use in templates.
    """

    @property
    def month_name(self):
        """
        Returns the name of the month in which the CompendiumEntry was published.
        Note that only the index of the month (1 to 12) is stored in the database
        and not the actual name of the month itself.
        """
        return month_name(self.month)

    @property
    def all_authors(self):
        """
        Retrieve a single string with all of the names of the authors of the compendium
        entry.
        """
        authors = self.authors.all()
        if len(authors) == 0:
            return None
        else:
            return ", ".join(str(auth) for auth in authors)

    class Meta:
        # Manually specify the table name for the database
        db_table = "compendium"


def slug_generator(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = unique_slug_generator(instance)


pre_save.connect(slug_generator, sender=CompendiumEntry)
