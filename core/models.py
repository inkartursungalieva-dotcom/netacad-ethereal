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
