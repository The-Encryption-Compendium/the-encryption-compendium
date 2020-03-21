from django.contrib import admin
from users.forms import UserAdminForm
from users.models import User


class UserAdmin(admin.ModelAdmin):
    form = UserAdminForm


admin.site.register(User, UserAdmin)
