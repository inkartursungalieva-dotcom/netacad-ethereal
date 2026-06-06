from django.contrib import admin
from .models import AuditLog

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'module', 'action', 'timestamp')
    list_filter = ('action', 'module', 'timestamp')
    search_fields = ('user__username', 'details')
    readonly_fields = ('user', 'module', 'action', 'details', 'timestamp')
