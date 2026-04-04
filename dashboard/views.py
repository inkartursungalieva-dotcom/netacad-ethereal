import csv
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from courses.models import Module, UserProgress, UserAnswer
from laboratory.models import LabProgress
from accounts.models import User, Notification
from django.core.exceptions import PermissionDenied
from django.utils import timezone
from django.db.models import Avg, Count, Q, Sum
from django.contrib import messages
from django.utils.text import slugify
from django.utils.translation import gettext as _
import random

def teacher_required(view_func):
    """Декоратор для проверки роли преподавателя"""
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and (request.user.role == 'teacher' or request.user.is_superuser):
            return view_func(request, *args, **kwargs)
        raise PermissionDenied
    return _wrapped_view

def student_required(view_func):
    """Декоратор для проверки роли студента"""
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and (request.user.role == 'student' or request.user.is_superuser):
            return view_func(request, *args, **kwargs)
        raise PermissionDenied
    return _wrapped_view

def get_course_progress(user):
    """Вспомогательная функция для получения прогресса курса"""
    modules = Module.objects.all().order_by('order')
    user_progress = UserProgress.objects.filter(user=user)
    completed_modules = [p.module.id for p in user_progress if p.is_completed]
    
    completed_count = 0
    for module in modules:
        if module.id in completed_modules:
            completed_count += 1
    
    total_count = modules.count()
    progress_percent = int((completed_count / total_count * 100)) if total_count > 0 else 0
    
    # Также добавляем количество непрочитанных уведомлений
    unread_notifications_count = Notification.objects.filter(user=user, is_read=False).count()
    
    return {
        'completed_count': completed_count,
        'total_count': total_count,
        'progress_percent': progress_percent,
        'unread_notifications_count': unread_notifications_count,
    }

@login_required
def dashboard_index(request):
    """Отображение главной страницы дашборда"""
    if request.user.role == 'teacher' or request.user.is_superuser:
        return redirect('dashboard:teacher_index')
    
    progress = get_course_progress(request.user)
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')[:5]
    
    # Расчет дополнительных стат
    total_time_seconds = UserProgress.objects.filter(user=request.user).aggregate(Sum('time_spent'))['time_spent__sum'] or 0
    total_time_hours = round(total_time_seconds / 3600, 1)
    
    # Количество пройденных модулей
    completed_modules = UserProgress.objects.filter(user=request.user, is_completed=True).count()
    
    # Последний активный модуль
    last_progress = UserProgress.objects.filter(user=request.user).order_by('-completed_at').first()
    next_module = None
    if last_progress:
        next_module = Module.objects.filter(order__gt=last_progress.module.order).order_by('order').first()
    if not next_module:
        next_module = Module.objects.order_by('order').first()

    context = {
        **progress,
        'notifications': notifications,
        'total_time_hours': total_time_hours,
        'completed_modules': completed_modules,
        'next_module': next_module,
    }
    return render(request, 'dashboard/index.html', context)

@login_required
@teacher_required
def teacher_dashboard_index(request):
    """Отображение главной страницы дашборда преподавателя"""
    total_students = User.objects.filter(role='student').count()
    
    # Расчет средней завершаемости
    total_modules = Module.objects.count()
    if total_modules > 0 and total_students > 0:
        completed_progress = UserProgress.objects.filter(is_completed=True).count()
        avg_completion = int((completed_progress / (total_modules * total_students)) * 100)
    else:
        avg_completion = 0
        
    # Активные сегодня
    active_today = User.objects.filter(role='student', last_login__date=timezone.now().date()).count()
    
    # Модуль 8 заявки (прогресс по последнему модулю)
    final_module = Module.objects.order_by('-order').first()
    final_requests = UserProgress.objects.filter(module=final_module).count() if final_module else 0
    
    # Успеваемость по модулям для графика
    module_performance = Module.objects.annotate(
        avg_score=Avg('user_progress__score')
    ).order_by('order')
    
    # Прогресс студентов для таблицы
    students_progress = User.objects.filter(role='student').annotate(
        current_module=Count('progress'), # Упрощенно
        avg_score=Avg('progress__score')
    )[:5]
    
    # Последняя активность
    recent_progress = UserProgress.objects.select_related('user', 'module').order_by('-completed_at')[:5]
    
    # Прогресс студентов для таблицы (переименовываем для соответствия шаблону)
    recent_students_progress = User.objects.filter(role='student').annotate(
        current_module=Count('progress'),
        avg_student_score=Avg('progress__score')
    ).order_by('-last_login')[:5]
    
    context = {
        'total_students': total_students,
        'avg_completion': avg_completion,
        'active_today': active_today,
        'module_8_submissions': final_requests, # Соответствие шаблону
        'module_performance': module_performance,
        'recent_students_progress': recent_students_progress, # Соответствие шаблону
        'recent_progress': recent_progress,
    }
    return render(request, 'dashboard/teacher_index.html', context)

@login_required
@teacher_required
def export_report(request):
    """Экспорт отчета о прогрессе студентов в формате CSV"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="netacademy_report_{timezone.now().strftime("%Y%m%d")}.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        _('Студент'), 
        _('Email'), 
        _('Модуль'), 
        _('Завершен'), 
        _('Баллы'), 
        _('Ошибки'), 
        _('Дата завершения')
    ])
    
    progress_data = UserProgress.objects.select_related('user', 'module').all()
    for p in progress_data:
        writer.writerow([
            p.user.username,
            p.user.email,
            p.module.name,
            _('Да') if p.is_completed else _('Нет'),
            f"{p.score}%",
            p.errors_count,
            p.completed_at.strftime("%Y-%m-%d %H:%M") if p.completed_at else ""
        ])
    
    return response

@login_required
@teacher_required
def students_list(request):
    """Список всех студентов для преподавателя"""
    students = User.objects.filter(role='student').annotate(
        completed_count=Count('progress', filter=Q(progress__is_completed=True)),
        avg_score=Avg('progress__score')
    ).order_by('username')
    
    total_modules = Module.objects.count()
    
    context = {
        'students': students,
        'total_modules': total_modules,
    }
    return render(request, 'dashboard/students_list.html', context)

@login_required
@teacher_required
def student_detail(request, user_id):
    """Детальная информация о прогрессе конкретного студента"""
    student = get_object_or_404(User, id=user_id, role='student')
    progress = UserProgress.objects.filter(user=student).select_related('module').order_by('module__order')
    
    context = {
        'student': student,
        'progress': progress,
    }
    return render(request, 'dashboard/student_detail.html', context)

@login_required
@teacher_required
def create_module(request):
    """Создание нового учебного модуля"""
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        order = request.POST.get('order', 1)
        video_url = request.POST.get('video_url')
        image = request.FILES.get('image')
        file = request.FILES.get('file')
        
        if name:
            slug = slugify(name, allow_unicode=True)
            if not slug or Module.objects.filter(slug=slug).exists():
                base_slug = slug or "module"
                slug = f"{base_slug}-{random.randint(100, 999)}"
                
            Module.objects.create(
                name=name,
                description=description,
                order=int(order) if order else 0,
                slug=slug,
                video_url=video_url,
                image=image,
                file=file
            )
            messages.success(request, _("Модуль '{}' успешно создан.").format(name))
            return redirect('dashboard:teacher_index')
            
    return render(request, 'dashboard/create_module.html')

@login_required
@teacher_required
def edit_module(request, module_id):
    """Редактирование существующего учебного модуля"""
    module = get_object_or_404(Module, id=module_id)
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        order = request.POST.get('order', module.order)
        video_url = request.POST.get('video_url')
        image = request.FILES.get('image')
        file = request.FILES.get('file')
        
        if name:
            module.name = name
            module.description = description
            module.order = int(order) if order else 0
            module.video_url = video_url
            
            if image:
                module.image = image
            if file:
                module.file = file
            
            if not module.slug:
                new_slug = slugify(name, allow_unicode=True)
                if not new_slug or Module.objects.filter(slug=new_slug).exists():
                    new_slug = f"{new_slug or 'module'}-{random.randint(100, 999)}"
                module.slug = new_slug
            
            # Помечаем модуль как измененный
            module.is_custom = True
                
            module.save()
            messages.success(request, _("Модуль '{}' успешно обновлен.").format(name))
            return redirect('courses:list')
            
    return render(request, 'dashboard/edit_module.html', {'module': module})

@login_required
@teacher_required
def reset_module_view(request, module_id):
    """Сброс модуля к исходному состоянию (очистка полей, добавленных через браузер)"""
    module = get_object_or_404(Module, id=module_id)
    
    # Очищаем поля, добавленные через админку/панель
    module.description = ""
    module.video_url = None
    
    # Удаляем файлы, если они есть
    if module.image:
        module.image.delete(save=False)
    if module.file:
        module.file.delete(save=False)
        
    module.is_custom = False
    module.save()
    
    messages.success(request, _("Модуль '{}' сброшен к исходному состоянию.").format(module.name))
    return redirect('dashboard:edit_module', module_id=module.id)

@login_required
@teacher_required
def delete_module(request, module_id):
    """Удаление учебного модуля"""
    module = get_object_or_404(Module, id=module_id)
    if request.method == 'POST':
        name = module.name
        module.delete()
        messages.success(request, _("Модуль '{}' успешно удален.").format(name))
        return redirect('courses:list')
    return render(request, 'dashboard/delete_module_confirm.html', {'module': module})

@login_required
@teacher_required
def mail_students(request):
    """Страница рассылки студентам"""
    if request.method == 'POST':
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        
        if subject and message:
            # Получаем всех студентов
            students = User.objects.filter(role='student')
            
            # Создаем уведомления для каждого студента
            notifications = [
                Notification(
                    user=student,
                    title=subject,
                    message=message
                ) for student in students
            ]
            Notification.objects.bulk_create(notifications)
            
            messages.success(request, _("Сообщение успешно отправлено всем студентам."))
            return redirect('dashboard:teacher_index')
        
    return render(request, 'dashboard/mail_students.html')

@login_required
def test_results_list(request):
    """Отображение страницы результатов тестов"""
    # Если это преподаватель или админ, показываем результаты всех студентов
    if request.user.role == 'teacher' or request.user.is_superuser:
        user_progress = UserProgress.objects.all().select_related('module', 'user').order_by('-completed_at')
        is_teacher = True
    else:
        # Для студента показываем только его результаты
        user_progress = UserProgress.objects.filter(user=request.user).select_related('module').order_by('-completed_at')
        is_teacher = False
        
    progress = get_course_progress(request.user)
    
    context = {
        'results': user_progress,
        'is_teacher': is_teacher,
        **progress
    }
    return render(request, 'dashboard/test_results.html', context)

@login_required
def support_view(request):
    """Отображение страницы поддержки"""
    progress = get_course_progress(request.user)
    context = {
        **progress
    }
    return render(request, 'dashboard/support.html', context)

@login_required
def grades_view(request):
    """Страница журнала оценок для студентов и преподавателей"""
    # Если это преподаватель или админ
    if request.user.role == 'teacher' or request.user.is_superuser:
        # Получаем всех студентов с их прогрессом и лабами
        students = User.objects.filter(role='student').prefetch_related('progress', 'lab_progress')
        total_modules = Module.objects.count()
        
        students_grades = []
        for student in students:
            # Расчет общего прогресса и среднего балла
            test_scores = [p.score for p in student.progress.all() if p.is_completed]
            lab_scores = [p.score for p in student.lab_progress.all() if p.is_completed]
            all_scores = test_scores + lab_scores
            
            # Средняя оценка за выполненные задания (100 баллов = 100%)
            avg_score = round(sum(all_scores) / len(all_scores)) if all_scores else 0
            
            # Считаем прогресс (учитываем и тесты, и лабы как шаги)
            completed_tests = student.progress.filter(is_completed=True).count()
            completed_labs = student.lab_progress.filter(is_completed=True).count()
            
            # Прогресс = (пройденные тесты + лабы) / (общее кол-во модулей * 2)
            progress_percent = int(((completed_tests + completed_labs) / (total_modules * 2)) * 100) if total_modules > 0 else 0
            
            # Последний активный модуль
            last_p = student.progress.order_by('-completed_at').first()
            current_module = last_p.module.name if last_p else _("Не начато")

            students_grades.append({
                'user': student,
                'avg_score': avg_score,
                'progress_percent': progress_percent,
                'current_module': current_module,
                'needs_attention': avg_score < 60 and (completed_tests > 0 or completed_labs > 0)
            })

        # Общая аналитика для карточек
        all_avg_scores = [s['avg_score'] for s in students_grades if s['progress_percent'] > 0]
        class_avg = round(sum(all_avg_scores) / len(all_avg_scores)) if all_avg_scores else 0
        needs_attention_count = sum(1 for s in students_grades if s['needs_attention'])

        context = {
            'is_teacher': True,
            'students_grades': students_grades,
            'total_modules_count': total_modules,
            'class_avg': class_avg,
            'needs_attention_count': needs_attention_count,
        }
    else:
        # Для студента - его собственные оценки
        test_progress = UserProgress.objects.filter(user=request.user).select_related('module')
        lab_progress = LabProgress.objects.filter(user=request.user).select_related('lab', 'lab__module')
        
        test_map = {p.module_id: p for p in test_progress}
        lab_map = {p.lab.module_id: p for p in lab_progress}
        
        modules = Module.objects.all().order_by('order')
        grades = []
        for module in modules:
            test = test_map.get(module.id)
            lab = lab_map.get(module.id)
            grades.append({
                'module': module,
                'test_score': test.score if test else '-',
                'test_completed': test.is_completed if test else False,
                'lab_score': lab.score if lab else '-',
                'lab_completed': lab.is_completed if lab else False,
            })
            
        context = {
            'is_teacher': False,
            'grades': grades,
            **get_course_progress(request.user)
        }
        
    return render(request, 'dashboard/grades.html', context)
