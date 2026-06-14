from django.db import models
from django.conf import settings
from courses.models import Module
from django.utils.translation import gettext_lazy as _

class Lab(models.Model):
    CATEGORY_CHOICES = [
        ('basic', _('Основы')),
        ('intermediate', _('Продвинутый')),
        ('advanced', _('Эксперт')),
    ]
    
    DIFFICULTY_CHOICES = [
        ('easy', _('Лёгкий')),
        ('medium', _('Средний')),
        ('hard', _('Сложный')),
    ]
    
    module = models.OneToOneField(Module, on_delete=models.CASCADE, related_name='lab', verbose_name=_("Модуль"))
    title = models.CharField(max_length=200, verbose_name=_("Заголовок"))
    title_kk = models.CharField(max_length=200, verbose_name=_("Заголовок (каз)"), null=True, blank=True)
    description = models.TextField(verbose_name=_("Описание"))
    description_kk = models.TextField(verbose_name=_("Описание (каз)"), null=True, blank=True)
    hints = models.TextField(blank=True, null=True, verbose_name=_("Подсказки"), help_text=_("Подсказки по командам терминала"))
    scenario_data = models.JSONField(verbose_name=_("Данные сценария"), help_text=_("Конфигурация симуляции (узлы, связи, команды)"))
    
    # Новые поля для расширения функционала
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='basic', verbose_name=_("Категория"))
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default='easy', verbose_name=_("Сложность"))
    estimated_time = models.IntegerField(default=30, verbose_name=_("Оценочное время (мин)"), help_text=_("Оценочное время выполнения в минутах"))
    order = models.IntegerField(default=0, verbose_name=_("Порядок"), help_text=_("Порядок отображения в списке"))
    tags = models.CharField(max_length=200, blank=True, verbose_name=_("Теги"), help_text=_("Теги через запятую, например: OSI, IP, Routing"))
    is_active = models.BooleanField(default=True, verbose_name=_("Активна?"))
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Дата создания"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Дата обновления"))

    class Meta:
        verbose_name = _("Лабораторная работа")
        verbose_name_plural = _("Лабораторные работы")
        ordering = ['order', 'id']

    def __str__(self):
        return f"{self.title} ({self.module.name})"
    
    def get_tags_list(self):
        """Возвращает список тегов"""
        return [tag.strip() for tag in self.tags.split(',') if tag.strip()] if self.tags else []

class LabProgress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='lab_progress', verbose_name=_("Пользователь"))
    lab = models.ForeignKey(Lab, on_delete=models.CASCADE, verbose_name=_("Лабораторная работа"))
    is_completed = models.BooleanField(default=False, verbose_name=_("Завершено?"), db_index=True)
    score = models.IntegerField(default=0, verbose_name=_("Баллы"))
    commands_history = models.JSONField(default=list, verbose_name=_("История команд"))
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Дата завершения"))
    
    # Новые поля для отслеживания прогресса
    attempts = models.IntegerField(default=0, verbose_name=_("Количество попыток"))
    started_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Дата начала"))
    last_activity = models.DateTimeField(null=True, blank=True, verbose_name=_("Последняя активность"))
    time_spent = models.IntegerField(default=0, verbose_name=_("Время затрачено (сек)"))

    class Meta:
        verbose_name = _("Прогресс лабы")
        verbose_name_plural = _("Прогресс лаб")
        unique_together = ('user', 'lab')
        ordering = ['-last_activity']

    def __str__(self):
        return f"{self.user.username} - {self.lab.title}"
    
    def save(self, *args, **kwargs):
        # Автоматически обновляем last_activity при каждом сохранении
        from django.utils import timezone
        self.last_activity = timezone.now()
        
        # Если это первая попытка и нет даты начала, устанавливаем её
        if self.attempts == 0 and not self.started_at:
            self.started_at = timezone.now()
        
        self.attempts += 1
        super().save(*args, **kwargs)
