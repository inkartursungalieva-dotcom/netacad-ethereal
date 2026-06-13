"""
Template filters для проверки ролей пользователей.
Упрощает логику проверки ролей в шаблонах.
"""

from django import template

register = template.Library()


@register.filter
def is_teacher(user):
    """Проверяет, является ли пользователь преподавателем или суперпользователем"""
    if not user or not user.is_authenticated:
        return False
    return user.role == 'teacher' or user.is_superuser


@register.filter
def is_student(user):
    """Проверяет, является ли пользователь студентом"""
    if not user or not user.is_authenticated:
        return False
    return user.role == 'student' or user.is_superuser


@register.filter
def is_admin(user):
    """Проверяет, является ли пользователь суперпользователем"""
    if not user or not user.is_authenticated:
        return False
    return user.is_superuser
