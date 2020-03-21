from django.contrib import admin
from research_assistant.models import CompendiumEntry
from research_assistant.forms import UserAdminForm, CompendiumEntryForm
from users.models import User

"""
---------------------------------------------------
Admin models
---------------------------------------------------
"""


class UserAdmin(admin.ModelAdmin):
    form = UserAdminForm


class CompendiumEntryAdmin(admin.ModelAdmin):
    form = CompendiumEntryForm


# Register your models here.
admin.site.register(User, UserAdmin)
admin.site.register(CompendiumEntry, CompendiumEntryAdmin)
