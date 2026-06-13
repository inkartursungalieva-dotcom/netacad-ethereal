from django.contrib import admin
from .models import AuditLog, AIConversation, AIMessage

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'module', 'action', 'timestamp')
    list_filter = ('action', 'module', 'timestamp')
    search_fields = ('user__username', 'details')
    readonly_fields = ('user', 'module', 'action', 'details', 'timestamp')

class AIMessageInline(admin.TabularInline):
    model = AIMessage
    extra = 0
    readonly_fields = ('role', 'content', 'timestamp')

@admin.register(AIConversation)
class AIConversationAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('user__username', 'title')
    inlines = [AIMessageInline]
    readonly_fields = ('user', 'created_at', 'updated_at')

@admin.register(AIMessage)
class AIMessageAdmin(admin.ModelAdmin):
    list_display = ('conversation', 'role', 'timestamp', 'content_preview')
    list_filter = ('role', 'timestamp')
    search_fields = ('conversation__user__username', 'content')
    readonly_fields = ('conversation', 'role', 'content', 'timestamp')

    def content_preview(self, obj):
        return obj.content[:50] + ('...' if len(obj.content) > 50 else '')
    content_preview.short_description = 'Содержание'
