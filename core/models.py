from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

class AuditLog(models.Model):
    """Логирование действий студентов во время тестов"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='audit_logs', verbose_name=_('Студент'))
    module = models.ForeignKey('courses.Module', on_delete=models.CASCADE, verbose_name=_('Модуль'))
    action = models.CharField(max_length=255, verbose_name=_('Действие'))
    details = models.TextField(blank=True, null=True, verbose_name=_('Детали'))
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name=_('Время'))

    class Meta:
        verbose_name = _('Лог аудита')
        verbose_name_plural = _('Логи аудита')
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.user.username} - {self.action} - {self.timestamp}"


class AIConversation(models.Model):
    """История диалогов с ИИ-помощником"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ai_conversations', verbose_name=_('Пользователь'))
    title = models.CharField(max_length=255, blank=True, null=True, verbose_name=_('Название диалога'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Создано'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Обновлено'))

    class Meta:
        verbose_name = _('Диалог ИИ')
        verbose_name_plural = _('Диалоги ИИ')
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.user.username} - {self.title or 'Без названия'} ({self.created_at.strftime('%d.%m.%Y %H:%M')})"


class AIMessage(models.Model):
    """Отдельные сообщения в диалогах с ИИ"""
    ROLE_CHOICES = [
        ('user', _('Пользователь')),
        ('assistant', _('ИИ-помощник')),
    ]

    conversation = models.ForeignKey(AIConversation, on_delete=models.CASCADE, related_name='messages', verbose_name=_('Диалог'))
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, verbose_name=_('Роль'))
    content = models.TextField(verbose_name=_('Содержание'))
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name=_('Время'))

    class Meta:
        verbose_name = _('Сообщение ИИ')
        verbose_name_plural = _('Сообщения ИИ')
        ordering = ['timestamp']

    def __str__(self):
        return f"{self.get_role_display()} - {self.content[:50]}"
