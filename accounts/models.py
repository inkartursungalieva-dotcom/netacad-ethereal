from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    ROLE_CHOICES = [
        ('student', _('Студент')),
        ('teacher', _('Преподаватель')),
    ]
    
    LANGUAGE_CHOICES = [
        ('ru', _('Русский')),
        ('kk', _('Қазақша')),
    ]
    
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default='student',
        verbose_name=_('Роль')
    )
    
    language = models.CharField(
        max_length=2,
        choices=LANGUAGE_CHOICES,
        default='ru',
        verbose_name=_('Язык интерфейса')
    )
    
    avatar = models.ImageField(
        upload_to='avatars/',
        null=True,
        blank=True,
        verbose_name=_('Аватар')
    )
    
    bio = models.TextField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name=_('О себе')
    )
    
    email_verified = models.BooleanField(
        default=False,
        verbose_name=_('Email подтвержден')
    )
    
    verification_code = models.CharField(
        max_length=6,
        blank=True,
        null=True,
        verbose_name=_('Код подтверждения')
    )
    
    verification_code_expires = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name=_('Срок действия кода')
    )
    
    last_verification_sent = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name=_('Последняя отправка кода')
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Дата регистрации')
    )
    
    class Meta:
        verbose_name = _('Пользователь')
        verbose_name_plural = _('Пользователи')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

class Notification(models.Model):
    """Модель уведомлений для пользователей"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications', verbose_name=_('Пользователь'))
    title = models.CharField(max_length=255, verbose_name=_('Заголовок'))
    message = models.TextField(verbose_name=_('Сообщение'))
    is_read = models.BooleanField(default=False, verbose_name=_('Прочитано'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Дата создания'))

    class Meta:
        verbose_name = _('Уведомление')
        verbose_name_plural = _('Уведомления')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.user.username}"
        