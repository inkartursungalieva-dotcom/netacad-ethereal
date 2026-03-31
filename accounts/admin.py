from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Notification


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'role', 'language', 'email_verified', 'created_at']
    list_filter = ['role', 'language', 'email_verified', 'is_staff']
    search_fields = ['username', 'email']
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Дополнительно', {
            'fields': ('role', 'language', 'email_verified', 'verification_code', 'verification_code_expires', 'last_verification_sent', 'created_at')
        }),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Дополнительно', {
            'fields': ('role', 'language', 'email_verified')
        }),
    )
