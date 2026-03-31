from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils.translation import gettext as _
from .models import Module, Question, Choice, UserProgress, UserAnswer, Resource
from .forms import ResourceForm
from laboratory.models import LabProgress
import json

def get_user_course_progress(user):
    """Возвращает информацию о прогрессе пользователя по всем модулям"""
    modules = Module.objects.all().order_by('order')
    if not modules.exists():
        return [], 0, 0, 0

    # Прогресс тестов
    progress_map = {p.module_id: p for p in UserProgress.objects.filter(user=user)}
    completed_module_ids = {mid for mid, p in progress_map.items() if p.is_completed}
    
    # Прогресс лабораторных работ
    lab_progress_map = {p.lab.module_id: p for p in LabProgress.objects.filter(user=user).select_related('lab')}

    # Определяем доступность
    unlocked = True
    for module in modules:
        module.is_completed = module.id in completed_module_ids
        module.lab_completed = lab_progress_map.get(module.id).is_completed if lab_progress_map.get(module.id) else False
        module.is_accessible = unlocked
        if not module.is_completed:
            unlocked = False

    completed_count = len(completed_module_ids)
    total_count = modules.count()
    progress_percent = int((completed_count / total_count) * 100) if total_count > 0 else 0

    return modules, completed_count, total_count, progress_percent

def roadmap_view(request):
    """Страница с дорожной картой обучения"""
    modules = Module.objects.all().order_by('order')
    
    if request.user.is_authenticated:
        user_progress = {p.module_id: p for p in UserProgress.objects.filter(user=request.user)}
        completed_modules = {mid for mid, p in user_progress.items() if p.is_completed}
        
        unlocked = True
        for module in modules:
            module.is_completed = module.id in completed_modules
            module.is_accessible = unlocked
            if not module.is_completed:
                unlocked = False # Следующие модули будут заблокированы
    else:
        # Для анонимных пользователей доступен только первый модуль
        for i, module in enumerate(modules):
            module.is_accessible = (i == 0)
            module.is_completed = False
            
    return render(request, 'courses/roadmap.html', {'modules': modules})


def can_access_module(user, module):
    """Проверка: может ли пользователь получить доступ к модулю"""
    if user.is_staff or (hasattr(user, 'role') and user.role == 'teacher'):
        return True
    
    # Если это первый модуль, он всегда доступен
    if module.order == 1:
        return True
    
    # Иначе, проверяем завершен ли предыдущий модуль
    previous_module = Module.objects.filter(order__lt=module.order).order_by('-order').first()
    if not previous_module:
        return True
        
    progress = UserProgress.objects.filter(user=user, module=previous_module, is_completed=True).exists()
    return progress

@login_required
def course_list(request):
    """Список курсов с учетом прогресса (оптимизировано)"""
    modules, completed_count, total_count, progress_percent = get_user_course_progress(request.user)
    
    # Если это преподаватель, модули всегда доступны
    if request.user.role == 'teacher' or request.user.is_superuser:
        for m in modules:
            m.is_accessible = True
        
    return render(request, 'courses/list.html', {
        'modules': modules,
        'completed_count': completed_count,
        'total_count': total_count,
        'progress_percent': progress_percent,
    })

from django.template import TemplateDoesNotExist
from django.template.loader import get_template

@login_required
def module_detail_view(request, slug):
    """Просмотр урока модуля"""
    module = get_object_or_404(Module, slug=slug)
    
    if not can_access_module(request.user, module):
        messages.error(request, _("Вы не можете получить доступ к этому модулю, пока не завершите предыдущий."))
        return redirect('courses:list')
        
    # Если преподаватель добавил специальный контент (видео, фото, файлы), 
    # используем универсальный красивый шаблон. 
    # Иначе пытаемся найти специфичный статический шаблон.
    if module.video_url or module.image or module.file:
        template_name = 'courses/generic_module.html'
    else:
        template_name = f'courses/{slug.replace("-", "_")}.html'
        try:
            get_template(template_name)
        except TemplateDoesNotExist:
            template_name = 'courses/generic_module.html'
        
    return render(request, template_name, {'module': module})

@login_required
def module_test_view(request, slug):
    """Прохождение теста модуля"""
    module = get_object_or_404(Module, slug=slug)
    
    if not can_access_module(request.user, module):
        messages.error(request, _("Тест недоступен, пока не завершен предыдущий модуль."))
        return redirect('courses:list')
        
    questions = module.questions.all().prefetch_related('choices')
    
    if request.method == 'POST':
        # Проверка на читерство (если пришел флаг из JS)
        is_cheated = request.POST.get('cheated') == 'true'
        time_spent = int(request.POST.get('time_spent', 0))
        
        if is_cheated:
            # Если сжульничал, сохраняем попытку с 0 баллов, но не завершаем модуль
            UserProgress.objects.update_or_create(
                user=request.user, 
                module=module,
                defaults={'is_completed': False, 'score': 0, 'time_spent': time_spent}
            )
            messages.error(request, _("Тест аннулирован из-за переключения вкладки."))
            return redirect('courses:list')

        # Обработка результатов теста
        score = 0
        errors_count = 0
        total_questions = questions.count()
        
        # Удаляем старые ответы для этого пользователя и модуля перед сохранением новых
        UserAnswer.objects.filter(user=request.user, question__module=module).delete()
        
        for question in questions:
            choice_id = request.POST.get(f'question_{question.id}')
            if choice_id:
                choice = get_object_or_404(Choice, id=choice_id)
                is_correct = choice.is_correct
                if is_correct:
                    score += 1
                else:
                    errors_count += 1
                
                # Сохраняем ответ пользователя
                UserAnswer.objects.create(
                    user=request.user,
                    question=question,
                    choice=choice,
                    is_correct=is_correct
                )
            else:
                errors_count += 1 # Пропущенный вопрос считается ошибкой
        
        # Сохранение прогресса
        pass_percentage = settings.TEST_PASS_PERCENTAGE
        is_completed = (score / total_questions * 100 >= pass_percentage) if total_questions > 0 else True
        progress, created = UserProgress.objects.update_or_create(
            user=request.user, 
            module=module,
            defaults={
                'is_completed': is_completed, 
                'score': score,
                'time_spent': time_spent,
                'errors_count': errors_count
            }
        )
            
        if is_completed:
            messages.success(request, _("Тест пройден! Ваш результат: {}/{}").format(score, total_questions))
        else:
            messages.error(request, _("Тест не пройден. Ваш результат: {}/{}. Нужно минимум {}%.").format(score, total_questions, pass_percentage))
        
        return redirect('courses:test_results', slug=slug)

    return render(request, 'courses/module_test.html', {
        'module': module,
        'questions': questions
    })

@login_required
def test_results_view(request, slug):
    """Страница результатов теста"""
    module = get_object_or_404(Module, slug=slug)
    progress = get_object_or_404(UserProgress, user=request.user, module=module)
    user_answers = UserAnswer.objects.filter(user=request.user, question__module=module).select_related('question', 'choice')
    
    total_questions = module.questions.count()
    score_percent = int((progress.score / total_questions * 100)) if total_questions > 0 else 0
    
    # Расчет stroke-dashoffset для SVG кольца (базовое значение 263.89)
    stroke_dashoffset = 263.89 - (263.89 * score_percent / 100)
    
    # Форматирование времени
    mins = progress.time_spent // 60
    secs = progress.time_spent % 60
    time_formatted = f"{mins:02d}:{secs:02d}"
    
    # Следующий модуль
    next_module = Module.objects.filter(order__gt=module.order).order_by('order').first()
    
    # Сложность модуля (можно брать из первого вопроса или задать среднюю)
    module_difficulty = _("Средняя")
    if total_questions > 0:
        module_difficulty = user_answers.first().question.difficulty if user_answers.exists() else _("Средняя")

    return render(request, 'courses/test_results.html', {
        'module': module,
        'progress': progress,
        'user_answers': user_answers,
        'total_questions': total_questions,
        'score_percent': score_percent,
        'stroke_dashoffset': stroke_dashoffset,
        'time_formatted': time_formatted,
        'next_module': next_module,
        'module_difficulty': module_difficulty,
    })

@login_required
def resource_list_view(request):
    """Список учебных ресурсов (книги, документы)"""
    resources = Resource.objects.all().select_related('uploaded_by')
    
    # Фильтрация по типу, если передано в GET
    res_type = request.GET.get('type')
    if res_type in dict(Resource.RESOURCE_TYPES):
        resources = resources.filter(resource_type=res_type)
        
    context = {
        'resources': resources,
        'resource_types': Resource.RESOURCE_TYPES,
        'current_type': res_type
    }
    return render(request, 'courses/resources.html', context)

@login_required
def add_resource_view(request):
    """Добавление нового ресурса (только для преподавателей)"""
    # Проверка роли
    if not (request.user.role == 'teacher' or request.user.is_superuser):
        messages.error(request, _("У вас нет прав для добавления материалов."))
        return redirect('courses:resource_list')
        
    if request.method == 'POST':
        form = ResourceForm(request.POST, request.FILES)
        if form.is_valid():
            resource = form.save(commit=False)
            resource.uploaded_by = request.user
            resource.save()
            messages.success(request, _("Материал успешно добавлен!"))
            return redirect('courses:resource_list')
    else:
        form = ResourceForm()
        
    return render(request, 'courses/add_resource.html', {'form': form})

@login_required
def delete_resource_view(request, pk):
    """Удаление ресурса (только для преподавателей)"""
    if not (request.user.role == 'teacher' or request.user.is_superuser):
        return JsonResponse({'error': 'Permission denied'}, status=403)
        
    resource = get_object_or_404(Resource, pk=pk)
    resource.delete()
    messages.success(request, _("Материал удален."))
    return redirect('courses:resource_list')

