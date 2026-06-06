from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, authenticate, get_user_model
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext as _, activate
from django.utils import timezone
from django.utils import translation
from django.conf import settings
from django.core.mail import send_mail
import random
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

def get_course_progress(user):
    """Вспомогательная функция для получения прогресса курса (оптимизированная)"""
    total_count = Module.objects.count()
    if total_count == 0:
        return {'completed_count': 0, 'total_count': 0, 'progress_percent': 0}

    completed_count = UserProgress.objects.filter(user=user, is_completed=True).count()
    
    progress_percent = int((completed_count / total_count) * 100)
    
    return {
        'completed_count': completed_count,
        'total_count': total_count,
        'progress_percent': progress_percent,
    }

@login_required
def profile_view(request):
    """Отображение и редактирование профиля пользователя"""
    progress = get_course_progress(request.user)
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


def register_view(request):
    """Обработка регистрации пользователя"""
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            
            # Генерация кода подтверждения (опционально)
            user.verification_code = str(random.randint(100000, 999999))
            user.verification_code_expires = timezone.now() + timezone.timedelta(hours=24)
            user.last_verification_sent = timezone.now()
            user.is_active = True  # Активируем пользователя
            
            user.save()
            
            messages.success(request, _('Регистрация успешна! Теперь вы можете войти.'))
            return redirect('accounts:login')
        else:
            messages.error(request, _('Пожалуйста, исправьте ошибки в форме.'))
    else:
        form = RegisterForm()
    
    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    """Обработка входа пользователя с 2FA"""
    if request.user.is_authenticated:
        if request.user.role == 'teacher' or request.user.is_superuser:
            return redirect('dashboard:teacher_index')
        return redirect('dashboard:index')
    
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            
            # 2FA: Генерируем код и сохраняем в сессии
            code = str(random.randint(100000, 999999))
            request.session['2fa_user_id'] = user.id
            request.session['2fa_code'] = code
            request.session['2fa_expiry'] = (timezone.now() + timezone.timedelta(minutes=10)).timestamp()
            
            # Отправляем код на Email
            try:
                send_mail(
                    _('Код подтверждения входа - Computer Networks'),
                    _('Ваш код для входа: {}').format(code),
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    fail_silently=True,
                )
                messages.info(request, _('Код подтверждения отправлен на ваш email.'))
                return redirect('accounts:verify_2fa')
            except Exception as e:
                # Если почта не настроена, для тестов можем залогинить сразу (но выводим инфо)
                if settings.DEBUG:
                    messages.warning(request, f"DEBUG: 2FA Code is {code}")
                    return redirect('accounts:verify_2fa')
                messages.error(request, _('Ошибка при отправке email. Попробуйте позже.'))
        else:
            # Ошибки уже добавлены в форму
            messages.error(request, _('Неверный email или пароль.'))
    else:
        form = CustomAuthenticationForm()
    
    return render(request, 'accounts/login.html', {'form': form})

def verify_2fa_view(request):
    """Страница подтверждения 2FA кода"""
    user_id = request.session.get('2fa_user_id')
    if not user_id:
        return redirect('accounts:login')
        
    if request.method == 'POST':
        user_code = request.POST.get('code')
        saved_code = request.session.get('2fa_code')
        expiry = request.session.get('2fa_expiry', 0)
        
        if user_code == saved_code and timezone.now().timestamp() < expiry:
            user = get_object_or_404(User, id=user_id)
            login(request, user)
            
            # Установка языка из профиля пользователя в сессию и куки
            if user.language:
                request.session['_language'] = user.language
                translation.activate(user.language)

            # Очистка сессии от 2FA данных
            del request.session['2fa_user_id']
            del request.session['2fa_code']
            del request.session['2fa_expiry']
            
            messages.success(request, _('Добро пожаловать, {}!').format(user.username))
            
            response = None
            if user.role == 'teacher' or user.is_superuser:
                response = redirect('dashboard:teacher_index')
            else:
                response = redirect('dashboard:index')

            if user.language:
                cookie_name = getattr(settings, 'LANGUAGE_COOKIE_NAME', 'django_language')
                response.set_cookie(cookie_name, user.language)
            
            return response
        else:
            messages.error(request, _('Неверный или просроченный код.'))
            
    return render(request, 'accounts/verify_2fa.html')


@login_required
def verify_email_view(request):
    """Подтверждение email по коду"""
    if request.method == 'POST':
        code = request.POST.get('verification_code')
        user = request.user
        
        if user.verification_code == code and user.verification_code_expires > timezone.now():
            user.email_verified = True
            user.verification_code = ''
            user.verification_code_expires = None
            user.save()
            messages.success(request, _('Email успешно подтверждён!'))
            return redirect('home')
        else:
            messages.error(request, _('Неверный или просроченный код.'))
    
    return render(request, 'accounts/verify_email.html')


@login_required
def resend_verification_view(request):
    """Повторная отправка кода подтверждения"""
    user = request.user
    
    # Ограничение частоты отправки (1 раз в 5 минут)
    if user.last_verification_sent:
        time_diff = timezone.now() - user.last_verification_sent
        if time_diff.total_seconds() < 300:  # 5 минут
            messages.warning(request, _('Подождите перед повторной отправкой.'))
            return redirect('accounts:verify_email')
    
    # Генерация нового кода
    user.verification_code = str(random.randint(100000, 999999))
    user.verification_code_expires = timezone.now() + timezone.timedelta(hours=24)
    user.last_verification_sent = timezone.now()
    user.save()
    
    # Отправка письма
    send_verification_email(user)
    
    messages.success(request, _('Новый код отправлен на ваш email.'))
    return redirect('accounts:verify_email')

def send_verification_email(user):
    """Отправляет email с кодом подтверждения (заглушка)"""
    # В реальном проекте здесь будет логика отправки email
    # Например, с использованием Django send_mail или Celery
    print(f"Sending verification email to {user.email} with code {user.verification_code}")