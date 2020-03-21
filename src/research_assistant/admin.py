from django.contrib import admin
from research_assistant.models import CompendiumEntry
from research_assistant.forms import CompendiumEntryForm


class CompendiumEntryAdmin(admin.ModelAdmin):
    form = CompendiumEntryForm


admin.site.register(CompendiumEntry, CompendiumEntryAdmin)
