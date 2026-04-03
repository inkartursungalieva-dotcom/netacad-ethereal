from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from courses.models import Module

class Lab(models.Model):
    """Модель лабораторной работы (практики)"""
    module = models.OneToOneField(Module, on_delete=models.CASCADE, related_name='lab', verbose_name=_("Модуль"))
    title = models.CharField(max_length=200, verbose_name=_("Заголовок"))
    description = models.TextField(verbose_name=_("Описание"))
    scenario_data = models.JSONField(verbose_name=_("Данные сценария"), help_text=_("Конфигурация симуляции (узлы, связи, команды)"))
    hints = models.TextField(blank=True, null=True, verbose_name=_("Подсказки"), help_text=_("Подсказки по командам терминала"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Дата создания"))

    class Meta:
        verbose_name = _("Лабораторная работа")
        verbose_name_plural = _("Лабораторные работы")

    def __str__(self):
        return self.title

class LabProgress(models.Model):
    """Модель прогресса прохождения лабораторной работы"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='lab_progress', verbose_name=_("Пользователь"))
    lab = models.ForeignKey(Lab, on_delete=models.CASCADE, verbose_name=_("Лабораторная работа"))
    is_completed = models.BooleanField(default=False, verbose_name=_("Завершено?"))
    score = models.IntegerField(default=0, verbose_name=_("Баллы"))
    commands_history = models.JSONField(default=list, verbose_name=_("История команд"))
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Дата завершения"))

    class Meta:
        verbose_name = _("Прогресс лабы")
        verbose_name_plural = _("Прогресс лаб")

    def __str__(self):
        return f"{self.user.username} - {self.lab.title}"
