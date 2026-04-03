from django.contrib import admin
from .models import Lab, LabProgress

@admin.register(Lab)
class LabAdmin(admin.ModelAdmin):
    list_display = ('title', 'module', 'created_at')
    search_fields = ('title', 'module__name')

@admin.register(LabProgress)
class LabProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'lab', 'is_completed', 'score', 'completed_at')
    list_filter = ('is_completed', 'lab')