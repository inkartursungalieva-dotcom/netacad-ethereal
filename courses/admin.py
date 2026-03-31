from django.contrib import admin
from .models import Module, Question, Choice, UserAnswer, UserProgress, Resource

@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ('title', 'resource_type', 'uploaded_by', 'created_at')
    list_filter = ('resource_type', 'uploaded_by')
    search_fields = ('title', 'description')

@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ('order', 'name', 'slug')
    list_display_links = ('name',)
    ordering = ('order',)

class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 4

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'module', 'difficulty', 'category')
    list_filter = ('module', 'difficulty', 'category')
    inlines = [ChoiceInline]

@admin.register(Choice)
class ChoiceAdmin(admin.ModelAdmin):
    list_display = ('text', 'question', 'is_correct')
    list_filter = ('is_correct', 'question__module')

@admin.register(UserAnswer)
class UserAnswerAdmin(admin.ModelAdmin):
    list_display = ('user', 'question', 'choice', 'is_correct')
    list_filter = ('is_correct', 'user')

@admin.register(UserProgress)
class UserProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'module', 'is_completed', 'score', 'completed_at')
    list_filter = ('is_completed', 'module', 'user')