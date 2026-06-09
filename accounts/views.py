from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.contrib import messages
from django.contrib.auth import login, authenticate, get_user_model
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.translation import gettext as _, activate
from django.utils import timezone
from django.utils import translation
from django.conf import settings
from django.core.mail import send_mail
from django.http import JsonResponse
import random
import json
from .forms import RegisterForm, CustomAuthenticationForm, ProfileForm
from courses.models import Module, UserProgress
from laboratory.models import LabProgress, Lab
from .models import Notification

User = get_user_model()

@login_required
def notifications_view(request):
    """Отображение уведомлений пользователя"""
    notifications = Notification.objects.filter(user=request.user)
    
    # Помечаем все уведомления как прочитанные при открытии страницы
    notifications.filter(is_read=False).update(is_read=True)
    
    context = {
        'notifications': notifications,
    }
    return render(request, 'accounts/notifications.html', context)

@login_required
def mark_notification_read_view(request, pk):
    """Пометка конкретного уведомления как прочитанного"""
    notification = Notification.objects.filter(user=request.user, pk=pk).first()
    if notification:
        notification.is_read = True
        notification.save()
    return redirect('accounts:notifications')

def change_language_view(request):
    """Смена языка интерфейса и сохранение в профиле (если авторизован)"""
    if request.method == 'POST':
        lang_code = request.POST.get('language')
        next_url = request.POST.get('next', 'home')
        
        # Защита от Open Redirect (Critical 3)
        if not url_has_allowed_host_and_scheme(
            url=next_url,
            allowed_hosts={request.get_host()},
            require_https=request.is_secure(),
        ):
            next_url = 'home'
        
        if lang_code in dict(settings.LANGUAGES):
            # 1. Активируем язык в текущем потоке
            translation.activate(lang_code)
            
            # 2. Сохраняем в сессии (стандартный ключ Django - '_language')
            request.session['_language'] = lang_code
            
            # 3. Сохраняем в профиле пользователя (если авторизован)
            if request.user.is_authenticated:
                user = request.user
                user.language = lang_code
                user.save()
            
            response = redirect(next_url)
            # 4. Устанавливаем куки для LocaleMiddleware
            # Стандартное имя куки - 'django_language'
            cookie_name = getattr(settings, 'LANGUAGE_COOKIE_NAME', 'django_language')
            response.set_cookie(cookie_name, lang_code)
            return response
        
        return redirect(next_url)
    return redirect('home')

@login_required
def profile_view(request):
    """Отображение и редактирование профиля пользователя"""
    progress = request.user.get_course_progress()
    user_progress_all = UserProgress.objects.filter(user=request.user).select_related('module').order_by('module__order')
    
    # Данные для графика успеваемости
    progress_chart_labels = [p.module.name for p in user_progress_all]
    progress_chart_data = [p.score for p in user_progress_all]
    
    # Статистика по лабораториям
    user_lab_stats = []
    total_lab_time = 0
    
    # Получаем ID модулей, у которых есть лабораторные работы, одним запросом
    lab_module_ids = set(Lab.objects.values_list('module_id', flat=True))
    
    for p in user_progress_all:
        if p.module_id in lab_module_ids:
            time_spent_min = round(p.time_spent / 60, 1)
            user_lab_stats.append({
                'name': p.module.name,
                'time_spent': time_spent_min,
            })
            total_lab_time += time_spent_min
            
    # Расчет процента для прогресс-баров
    for stat in user_lab_stats:
        stat['percentage'] = (stat['time_spent'] / total_lab_time * 100) if total_lab_time > 0 else 0
    
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, _('Профиль успешно обновлён!'))
            return redirect('accounts:profile')
        else:
            messages.error(request, _('Пожалуйста, исправьте ошибки в форме.'))
    else:
        form = ProfileForm(instance=request.user)
    
    context = {
        'form': form,
        'user_lab_stats': user_lab_stats,
        'progress_chart_labels': progress_chart_labels,
        'progress_chart_data': progress_chart_data,
        **progress
    }
    return render(request, 'accounts/profile.html', context)


@ensure_csrf_cookie
def register_view(request):
    """Обработка регистрации пользователя (максимально надежная версия)"""
    if request.user.is_authenticated:
        return redirect('dashboard:index')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            try:
                user = form.save(commit=False)
                user.is_active = True
                user.email_verified = True
                user.save()
                
                # Стандартный способ логина
                login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                
                messages.success(request, _('Регистрация прошла успешно!'))
                
                # Редирект с полным путем
                if user.role == 'teacher' or user.is_superuser:
                    return redirect('/dashboard/teacher/')
                return redirect('/dashboard/')
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"CRITICAL REGISTRATION ERROR: {str(e)}", exc_info=True)
                messages.error(request, _('Внутренняя ошибка сервера. Попробуйте еще раз.'))
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = RegisterForm()
    
    return render(request, 'accounts/register.html', {'form': form})


@ensure_csrf_cookie
def login_view(request):
    """Обработка входа пользователя (максимально надежная версия)"""
    if request.user.is_authenticated:
        return redirect('dashboard:index')
    
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            try:
                user = form.get_user()
                login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                
                messages.success(request, _('Добро пожаловать!'))
                
                if user.role == 'teacher' or user.is_superuser:
                    response = redirect('/dashboard/teacher/')
                else:
                    response = redirect('/dashboard/')

                if user.language:
                    cookie_name = getattr(settings, 'LANGUAGE_COOKIE_NAME', 'django_language')
                    response.set_cookie(cookie_name, user.language)
                
                return response
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"CRITICAL LOGIN ERROR: {str(e)}", exc_info=True)
                messages.error(request, _('Внутренняя ошибка сервера при входе.'))
        else:
            messages.error(request, _('Неверный email или пароль.'))
    else:
        form = CustomAuthenticationForm()
    
    return render(request, 'accounts/login.html', {'form': form})

# Функции подтверждения email и 2FA удалены по просьбе пользователя (упрощенный вход)

def send_verification_email(user):
    """Отправляет email с кодом подтверждения (заглушка)"""
    # В реальном проекте здесь будет логика отправки email
    # Например, с использованием Django send_mail или Celery
    print(f"Sending verification email to {user.email} with code {user.verification_code}")