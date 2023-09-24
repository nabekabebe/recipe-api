"""
Django admin site customizations.
"""


from core import models
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib import admin
from django.utils.translation import gettext_lazy as _


class UserAdmin(BaseUserAdmin):
    """ Define admin pages for user model """

    ordering = ['id']
    list_display = ['email', 'name']

    fieldsets = [
        (None, {'fields': ('email', 'password')}),
        (_("Permissions"), { 'fields': ('is_staff', 'is_active', 'is_superuser') }),
        (_("Logins"), { 'fields': ('last_login',) }),
    ]

    readonly_fields = ['last_login']

    add_fieldsets = [
        (None, {
            'classes' : ('wide', 'extrapretty', 'extravolant'),
            'fields': ('name', 'email', 'password1', 'password2')
        }),
        (_("Permissions"), { 'fields': ('is_staff', 'is_active', 'is_superuser') }),
    ]


admin.site.register(models.User, UserAdmin)