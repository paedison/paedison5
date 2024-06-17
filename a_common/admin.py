from django.contrib import admin

from . import models


@admin.register(models.User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'email', 'is_admin', 'is_staff', 'joined_at', 'last_login')
