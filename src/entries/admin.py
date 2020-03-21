"""
Model administration through the Django admin interface
"""

from django.contrib import admin
from entries.models import CompendiumEntry
from research_assistant.forms import CompendiumEntryForm


class CompendiumEntryAdmin(admin.ModelAdmin):
    form = CompendiumEntryForm


admin.site.register(CompendiumEntry, CompendiumEntryAdmin)
