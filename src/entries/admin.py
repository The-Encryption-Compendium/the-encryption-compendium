"""
Model administration through the Django admin interface
"""

from django.contrib import admin
from entries.forms import CompendiumEntryForm
from entries.models import CompendiumEntry


class CompendiumEntryAdmin(admin.ModelAdmin):
    form = CompendiumEntryForm


admin.site.register(CompendiumEntry, CompendiumEntryAdmin)
