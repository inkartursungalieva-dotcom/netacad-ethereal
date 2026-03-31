from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

class Module(models.Model):
    """Модель модуля курса (Введение, Модель OSI и т.д.)"""
    name = models.CharField(max_length=255, verbose_name=_("Название модуля"))
    slug = models.SlugField(unique=True, verbose_name=_("Слаг"))
    order = models.PositiveIntegerField(default=0, verbose_name=_("Порядок"))
    description = models.TextField(blank=True, verbose_name=_("Описание"))
    image = models.ImageField(upload_to='modules/images/', null=True, blank=True, verbose_name=_("Изображение модуля"))
    video_url = models.URLField(max_length=500, null=True, blank=True, verbose_name=_("Ссылка на видео (YouTube)"))
    file = models.FileField(upload_to='modules/files/', null=True, blank=True, verbose_name=_("Дополнительный файл"))
    is_custom = models.BooleanField(default=False, verbose_name=_("Изменен преподавателем"))
    
    class Meta:
        verbose_name = _("Модуль")
        verbose_name_plural = _("Модули")
        ordering = ['order']

    def __str__(self):
        return f"{self.order}. {self.name}"


class Question(models.Model):
    """Модель вопроса теста"""
    DIFFICULTY_CHOICES = [
        ('Easy', _('Легкий')),
        ('Intermediate', _('Средний')),
        ('Hard', _('Сложный')),
    ]
    CATEGORY_CHOICES = [
        ('Conceptual Analysis', _('Концептуальный анализ')),
        ('Practical Application', _('Практическое применение')),
        ('Troubleshooting', _('Поиск неисправностей')),
    ]
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='questions', verbose_name=_("Модуль"))
    text = models.TextField(verbose_name=_("Текст вопроса"))
    hint = models.TextField(blank=True, null=True, verbose_name=_("Подсказка"))
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default='Intermediate', verbose_name=_("Сложность"))
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='Conceptual Analysis', verbose_name=_("Категория"))
    
    class Meta:
        verbose_name = _("Вопрос")
        verbose_name_plural = _("Вопросы")

    def __str__(self):
        return self.text[:50]


class Choice(models.Model):
    """Модель варианта ответа"""
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices', verbose_name=_("Вопрос"))
    text = models.CharField(max_length=255, verbose_name=_("Текст ответа"))
    is_correct = models.BooleanField(default=False, verbose_name=_("Верный?"))
    
    class Meta:
        verbose_name = _("Вариант ответа")
        verbose_name_plural = _("Варианты ответа")

    def __str__(self):
        return self.text


class UserProgress(models.Model):
    """Модель прогресса пользователя"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='progress', verbose_name=_("Пользователь"))
    module = models.ForeignKey(Module, on_delete=models.CASCADE, verbose_name=_("Модуль"))
    is_completed = models.BooleanField(default=False, verbose_name=_("Завершен?"))
    score = models.PositiveIntegerField(default=0, verbose_name=_("Баллы за тест"))
    time_spent = models.PositiveIntegerField(default=0, verbose_name=_("Время (в секундах)"))
    errors_count = models.PositiveIntegerField(default=0, verbose_name=_("Количество ошибок"))
    completed_at = models.DateTimeField(auto_now=True, verbose_name=_("Дата завершения"))
    
    class Meta:
        verbose_name = _("Прогресс пользователя")
        verbose_name_plural = _("Прогресс пользователей")
        unique_together = ('user', 'module')

    def __str__(self):
        status = _('Завершен') if self.is_completed else _('В процессе')
        return f"{self.user.username} - {self.module.name} ({status})"

    @property
    def score_percent(self):
        """Возвращает процент правильных ответов"""
        total = self.module.questions.count()
        if total > 0:
            return int((self.score / total) * 100)
        return 0


class UserAnswer(models.Model):
    """Модель ответа пользователя на конкретный вопрос"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=_("Пользователь"))
    question = models.ForeignKey(Question, on_delete=models.CASCADE, verbose_name=_("Вопрос"))
    choice = models.ForeignKey(Choice, on_delete=models.CASCADE, verbose_name=_("Выбранный ответ"))
    is_correct = models.BooleanField(default=False, verbose_name=_("Верно?"))
    
    class Meta:
        verbose_name = _("Ответ пользователя")
        verbose_name_plural = _("Ответы пользователей")
        unique_together = ('user', 'question')


class Resource(models.Model):
    """Модель для учебных материалов (книги, файлы)"""
    RESOURCE_TYPES = [
        ('book', _('Книга')),
        ('document', _('Документ')),
        ('presentation', _('Презентация')),
        ('other', _('Другое')),
    ]
    
    title = models.CharField(max_length=255, verbose_name=_("Заголовок"))
    description = models.TextField(blank=True, verbose_name=_("Описание"))
    file = models.FileField(upload_to='resources/', verbose_name=_("Файл"))
    resource_type = models.CharField(max_length=20, choices=RESOURCE_TYPES, default='book', verbose_name=_("Тип ресурса"))
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='uploaded_resources', verbose_name=_("Загрузил"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Дата загрузки"))
    
    class Meta:
        verbose_name = _("Ресурс")
        verbose_name_plural = _("Ресурсы")
        ordering = ['-created_at']

    def __str__(self):
        return self.title
