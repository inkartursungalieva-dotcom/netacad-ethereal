import csv
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from courses.models import Module, UserProgress, UserAnswer, Question, Choice, FinalProject
from laboratory.models import Lab, LabProgress
from accounts.models import User, Notification
from core.models import AuditLog
from network_simulator.models import NetworkTopology
from .forms import LabForm, QuestionForm, ChoiceFormSet
from django.db import transaction
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


@login_required
@teacher_required
def projects_list(request):
    """Список всех финальных проектов для преподавателя"""
    projects = FinalProject.objects.all().select_related('user', 'checked_by').order_by('-created_at')
    return render(request, 'dashboard/projects_list.html', {'projects': projects})


@login_required
@teacher_required
def project_detail(request, project_id):
    """Детальная информация о проекте для проверки"""
    project = get_object_or_404(FinalProject, id=project_id)
    if request.method == 'POST':
        status = request.POST.get('status')
        feedback = request.POST.get('feedback', '')
        
        if status:
            project.status = status
            project.feedback = feedback
            project.checked_by = request.user
            project.save()
            messages.success(request, _('Статус проекта обновлен!'))
            return redirect('dashboard:projects_list')
    
    return render(request, 'dashboard/project_detail.html', {'project': project})

@login_required
def dashboard_index(request):
    """Отображение главной страницы дашборда"""
    # Перенаправление на онбординг для новых пользователей
    if not request.user.completed_onboarding:
        return redirect('onboarding_welcome')
    
    if request.user.role == 'teacher' or request.user.is_superuser:
        return redirect('dashboard:teacher_index')
    
    progress = request.user.get_course_progress()
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
    
    # Последний проект пользователя
    user_project = FinalProject.objects.filter(user=request.user).order_by('-created_at').first()

    context = {
        **progress,
        'notifications': notifications,
        'total_time_hours': total_time_hours,
        'completed_modules': completed_modules,
        'next_module': next_module,
        'user_project': user_project,
    }
    return render(request, 'dashboard/index.html', context)

@login_required
@teacher_required
def teacher_dashboard_index(request):
    """Отображение главной страницы дашборда преподавателя (новая версия)"""
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
    
    # Модуль 8 заявки
    final_module = Module.objects.order_by('-order').first()
    final_requests = UserProgress.objects.filter(module=final_module).count() if final_module else 0
    
    # Успеваемость по модулям
    module_perf = []
    try:
        module_perf = list(Module.objects.annotate(
            avg_score=Avg('user_progress__score'),
            completed_count=Count('user_progress', filter=Q(user_progress__is_completed=True))
        ).order_by('order'))
    except:
        module_perf = list(Module.objects.all().order_by('order'))
    
    # Прогресс студентов
    student_perf = []
    try:
        student_perf = list(User.objects.filter(role='student').annotate(
            current_module_count=Count('progress'),
            avg_student_score=Avg('progress__score')
        ).order_by('-last_login')[:5])
    except:
        student_perf = list(User.objects.filter(role='student').order_by('-last_login')[:5])
    
    recent_act = UserProgress.objects.filter(user__role='student').select_related('user', 'module').order_by('-completed_at')[:5]
    
    context = {
        'total_students': total_students,
        'avg_completion': avg_completion,
        'active_today': active_today,
        'module_8_submissions': final_requests,
        'module_performance': module_perf,
        'recent_students_progress': student_perf,
        'recent_progress': recent_act,
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
    
    progress_data = UserProgress.objects.filter(user__role='student').select_related('user', 'module').all()
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
    audit_logs = AuditLog.objects.filter(user=student).select_related('module').order_by('-timestamp')[:50]
    
    context = {
        'student': student,
        'progress': progress,
        'audit_logs': audit_logs,
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
                file=file,
                is_custom=True
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
            module.is_custom = True
            
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
        user_progress = UserProgress.objects.filter(user__role='student').select_related('module', 'user').order_by('-completed_at')
        is_teacher = True
    else:
        # Для студента показываем только его результаты
        user_progress = UserProgress.objects.filter(user=request.user).select_related('module').order_by('-completed_at')
        is_teacher = False
        
    progress = request.user.get_course_progress()

    results_with_percent = []
    for result in user_progress:
        # UserProgress model now has a @property score_percent
        # We don't need to manually calculate it here and assign to a non-existent setter
        results_with_percent.append(result)
    
    context = {
        'results': results_with_percent,
        'is_teacher': is_teacher,
        **progress
    }
    return render(request, 'dashboard/test_results.html', context)

@login_required
def support_view(request):
    """Отображение страницы поддержки"""
    progress = request.user.get_course_progress()
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
            **request.user.get_course_progress()
        }
        
    return render(request, 'dashboard/grades.html', context)

# --- Управление лабораторными работами ---

@login_required
@teacher_required
def labs_list(request):
    """Список всех лабораторных работ"""
    labs = Lab.objects.all().select_related('module').order_by('module__order')
    return render(request, 'dashboard/labs_list.html', {'labs': labs})

@login_required
@teacher_required
def create_lab(request):
    """Создание новой лабораторной работы"""
    if request.method == 'POST':
        form = LabForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, _("Лабораторная работа успешно создана."))
            return redirect('dashboard:labs_list')
    else:
        # Предзаполняем модуль, если он передан в GET
        module_id = request.GET.get('module')
        initial = {'module': module_id} if module_id else {}
        form = LabForm(initial=initial)
    return render(request, 'dashboard/create_lab.html', {'form': form})

@login_required
@teacher_required
def edit_lab(request, lab_id):
    """Редактирование лабораторной работы"""
    lab = get_object_or_404(Lab, id=lab_id)
    if request.method == 'POST':
        form = LabForm(request.POST, instance=lab)
        if form.is_valid():
            form.save()
            messages.success(request, _("Лабораторная работа успешно обновлена."))
            return redirect('dashboard:labs_list')
    else:
        form = LabForm(instance=lab)
    return render(request, 'dashboard/edit_lab.html', {'form': form, 'lab': lab})

@login_required
@teacher_required
def delete_lab(request, lab_id):
    """Удаление лабораторной работы"""
    lab = get_object_or_404(Lab, id=lab_id)
    if request.method == 'POST':
        title = lab.title
        lab.delete()
        messages.success(request, _("Лабораторная работа '{}' удалена.").format(title))
        return redirect('dashboard:labs_list')
    return render(request, 'dashboard/delete_lab_confirm.html', {'lab': lab})

# --- Управление вопросами тестов ---

@login_required
@teacher_required
def questions_list(request):
    """Список всех вопросов тестов"""
    questions = Question.objects.all().select_related('module').order_by('module__order', 'id')
    return render(request, 'dashboard/questions_list.html', {'questions': questions})

@login_required
@teacher_required
def create_question(request):
    """Создание нового вопроса с вариантами ответов"""
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        formset = ChoiceFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                question = form.save()
                formset.instance = question
                formset.save()
            messages.success(request, _("Вопрос успешно создан."))
            return redirect('dashboard:questions_list')
    else:
        # Предзаполняем модуль, если он передан в GET
        module_id = request.GET.get('module')
        initial = {'module': module_id} if module_id else {}
        form = QuestionForm(initial=initial)
        formset = ChoiceFormSet()
    return render(request, 'dashboard/create_question.html', {'form': form, 'formset': formset})

@login_required
@teacher_required
def edit_question(request, question_id):
    """Редактирование вопроса и его вариантов ответов"""
    question = get_object_or_404(Question, id=question_id)
    if request.method == 'POST':
        form = QuestionForm(request.POST, instance=question)
        formset = ChoiceFormSet(request.POST, instance=question)
        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                form.save()
                formset.save()
            messages.success(request, _("Вопрос успешно обновлен."))
            return redirect('dashboard:questions_list')
    else:
        form = QuestionForm(instance=question)
        formset = ChoiceFormSet(instance=question)
    return render(request, 'dashboard/edit_question.html', {'form': form, 'formset': formset, 'question': question})

@login_required
@teacher_required
def delete_question(request, question_id):
    """Удаление вопроса"""
    question = get_object_or_404(Question, id=question_id)
    if request.method == 'POST':
        question.delete()
        messages.success(request, _("Вопрос удален."))
        return redirect('dashboard:questions_list')
    return render(request, 'dashboard/delete_question_confirm.html', {'question': question})
