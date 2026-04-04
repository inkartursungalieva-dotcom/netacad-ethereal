from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
import uuid

class Module(models.Model):
    """Модель модуля обучения"""
    name = models.CharField(max_length=200, verbose_name=_("Название модуля"))
    slug = models.SlugField(unique=True, verbose_name=_("URL слаг"))
    description = models.TextField(verbose_name=_("Описание"))
    image = models.ImageField(upload_to='modules/', blank=True, null=True, verbose_name=_("Изображение"))
    video_url = models.URLField(
        max_length=500, blank=True, null=True, verbose_name=_("Ссылка на видео (YouTube)")
    )
    file = models.FileField(
        upload_to='modules/files/', blank=True, null=True, verbose_name=_("Дополнительный файл")
    )
    order = models.PositiveIntegerField(default=0, verbose_name=_("Порядок"))
    is_active = models.BooleanField(default=True, verbose_name=_("Активен?"))
    is_custom = models.BooleanField(default=False, verbose_name=_("Изменён преподавателем"))

    class Meta:
        verbose_name = _("Модуль")
        verbose_name_plural = _("Модули")
        ordering = ['order']

    @property
    def test_duration_minutes(self):
        """Возвращает время на тест в минутах в зависимости от количества вопросов"""
        return max(5, self.questions.count() * 1) # Минимум 5 минут, или по 1 минуте на вопрос

    def __str__(self):
        return self.name

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
    TYPE_CHOICES = [
        ('multiple_choice', _('Выбор варианта')),
        ('sorting', _('Сортировка')),
        ('matching', _('Сопоставление')),
        ('text_input', _('Ввод текста')),
    ]
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='questions', verbose_name=_("Модуль"), null=True, blank=True)
    text = models.TextField(verbose_name=_("Текст вопроса"))
    hint = models.TextField(blank=True, null=True, verbose_name=_("Подсказка"))
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default='Intermediate', verbose_name=_("Сложность"))
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='Conceptual Analysis', verbose_name=_("Категория"))
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='multiple_choice', verbose_name=_("Тип вопроса"))
    section = models.CharField(max_length=100, blank=True, null=True, verbose_name=_("Секция (блок)"))
    
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
    order = models.PositiveIntegerField(default=0, verbose_name=_("Порядок (для сортировки)"))
    pair_text = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("Пара (для сопоставления)"))
    
    class Meta:
        verbose_name = _("Вариант ответа")
        verbose_name_plural = _("Варианты ответа")
        ordering = ['order', 'id']

    def __str__(self):
        return self.text

class UserProgress(models.Model):
    """Модель прогресса пользователя в модуле"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user_progress', verbose_name=_("Пользователь"))
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='module_progress', verbose_name=_("Модуль"))
    score = models.PositiveIntegerField(default=0, verbose_name=_("Баллы"))
    time_spent = models.PositiveIntegerField(default=0, verbose_name=_("Затраченное время (сек)"))
    errors_count = models.PositiveIntegerField(default=0, verbose_name=_("Количество ошибок"))
    completed_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Дата завершения"))
    is_completed = models.BooleanField(default=False, verbose_name=_("Завершен?"))
    share_token = models.UUIDField(default=uuid.uuid4, null=True, blank=True, verbose_name=_("Токен доступа"))
    
    class Meta:
        verbose_name = _("Прогресс пользователя")
        verbose_name_plural = _("Прогресс пользователей")
        unique_together = ('user', 'module')

class UserAnswer(models.Model):
    """Модель ответа пользователя на конкретный вопрос"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=_("Пользователь"))
    question = models.ForeignKey(Question, on_delete=models.CASCADE, verbose_name=_("Вопрос"))
    choice = models.ForeignKey(Choice, on_delete=models.CASCADE, null=True, blank=True, verbose_name=_("Выбранный ответ"))
    user_input = models.TextField(null=True, blank=True, verbose_name=_("Ввод пользователя"))
    user_order = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Порядок пользователя"))
    matched_text = models.CharField(max_length=255, null=True, blank=True, verbose_name=_("Сопоставленный текст"))
    is_correct = models.BooleanField(default=False, verbose_name=_("Верно?"))
    
    class Meta:
        verbose_name = _("Ответ пользователя")
        verbose_name_plural = _("Ответы пользователей")

class UsabilityTest(models.Model):
    """Модель для оценки юзабилити по методике SUS"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=_("Пользователь"))
    q1 = models.PositiveSmallIntegerField(verbose_name=_("Я думаю, что я хотел бы часто использовать эту систему"))
    q2 = models.PositiveSmallIntegerField(verbose_name=_("Я нашел систему излишне сложной"))
    q3 = models.PositiveSmallIntegerField(verbose_name=_("Я думаю, что система была легкой в использовании"))
    q4 = models.PositiveSmallIntegerField(verbose_name=_("Я думаю, что мне понадобится помощь технического специалиста, чтобы пользоваться этой системой"))
    q5 = models.PositiveSmallIntegerField(verbose_name=_("Я нашел, что различные функции в этой системе были хорошо интегрированы"))
    q6 = models.PositiveSmallIntegerField(verbose_name=_("Я думаю, что в этой системе было слишком много несогласованности"))
    q7 = models.PositiveSmallIntegerField(verbose_name=_("Я бы вообразил, что большинство людей научатся пользоваться этой системой очень быстро"))
    q8 = models.PositiveSmallIntegerField(verbose_name=_("Я нашел систему очень громоздкой в использовании"))
    q9 = models.PositiveSmallIntegerField(verbose_name=_("Я чувствовал себя очень уверенно, пользуясь системой"))
    q10 = models.PositiveSmallIntegerField(verbose_name=_("Мне нужно было узнать много вещей, прежде чем я смог приступить к работе с этой системой"))
    comment = models.TextField(blank=True, null=True, verbose_name=_("Комментарии"))
    created_at = models.DateTimeField(auto_now_add=True)

    def sus_score(self):
        score = (self.q1 - 1) + (5 - self.q2) + (self.q3 - 1) + (5 - self.q4) + \
                (self.q5 - 1) + (5 - self.q6) + (self.q7 - 1) + (5 - self.q8) + \
                (self.q9 - 1) + (5 - self.q10)
        return score * 2.5

    class Meta:
        verbose_name = _("Оценка юзабилити")
        verbose_name_plural = _("Оценки юзабилити")

class Resource(models.Model):
    """Модель дополнительного ресурса модуля"""
    TYPE_CHOICES = [
        ('Video', _('Видео')),
        ('PDF', _('PDF документ')),
        ('Link', _('Внешняя ссылка')),
        ('Other', _('Другое')),
    ]
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='resources', verbose_name=_("Модуль"), null=True, blank=True)
    title = models.CharField(max_length=200, verbose_name=_("Заголовок"))
    file = models.FileField(upload_to='resources/', blank=True, null=True, verbose_name=_("Файл"))
    url = models.URLField(blank=True, null=True, verbose_name=_("Ссылка"))
    description = models.TextField(blank=True, null=True, verbose_name=_("Описание"))
    resource_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='Other', verbose_name=_("Тип ресурса"))
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, verbose_name=_("Загрузил"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Дата загрузки"))

    RESOURCE_TYPES = TYPE_CHOICES

    class Meta:
        verbose_name = _("Ресурс")
        verbose_name_plural = _("Ресурсы")

    def __str__(self):
        return self.title
