from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, FileResponse
from django.utils.translation import gettext as _
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import io
import os
from .models import Module, Question, Choice, UserAnswer, UserProgress, Resource, UsabilityTest
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
def usability_test_view(request):
    """Страница оценки юзабилити по методике SUS"""
    if request.method == 'POST':
        UsabilityTest.objects.create(
            user=request.user,
            q1=int(request.POST.get('q1')),
            q2=int(request.POST.get('q2')),
            q3=int(request.POST.get('q3')),
            q4=int(request.POST.get('q4')),
            q5=int(request.POST.get('q5')),
            q6=int(request.POST.get('q6')),
            q7=int(request.POST.get('q7')),
            q8=int(request.POST.get('q8')),
            q9=int(request.POST.get('q9')),
            q10=int(request.POST.get('q10')),
            comment=request.POST.get('comment', '')
        )
        return render(request, 'courses/usability_thanks.html')
    
    questions = [
        (_("Я думаю, что я хотел бы часто использовать эту систему"), 'q1'),
        (_("Я нашел систему излишне сложной"), 'q2'),
        (_("Я думаю, что система была легкой в использовании"), 'q3'),
        (_("Я думаю, что мне понадобится помощь технического специалиста, чтобы пользоваться этой системой"), 'q4'),
        (_("Я нашел, что различные функции в этой системе были хорошо интегрированы"), 'q5'),
        (_("Я думаю, что в этой системе было слишком много несогласованности"), 'q6'),
        (_("Я бы вообразил, что большинство людей научатся пользоваться этой системой очень быстро"), 'q7'),
        (_("Я нашел систему очень громоздкой в использовании"), 'q8'),
        (_("Я чувствовал себя очень уверенно, пользуясь системой"), 'q9'),
        (_("Мне нужно было узнать много вещей, прежде чем я смог приступить к работе с этой системой"), 'q10'),
    ]
    return render(request, 'courses/usability_test.html', {'sus_questions': questions})

@login_required
def export_pdf_view(request, slug):
    """Экспорт результатов в PDF"""
    module = get_object_or_404(Module, slug=slug)
    progress = get_object_or_404(UserProgress, user=request.user, module=module)
    
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    
    # Попробуем найти шрифт с кириллицей (стандартные не поддерживают)
    # На Render/Linux обычно есть DejaVuSans
    font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    if not os.path.exists(font_path):
        # Если локально на Windows
        font_path = "C:/Windows/Fonts/arial.ttf"
    
    try:
        pdfmetrics.registerFont(TTFont('DejaVuSans', font_path))
        p.setFont('DejaVuSans', 12)
    except:
        p.setFont('Helvetica', 12)

    p.drawString(100, height - 100, f"Результаты теста: {module.name}")
    p.drawString(100, height - 120, f"Студент: {request.user.get_full_name() or request.user.username}")
    p.drawString(100, height - 140, f"Оценка: {progress.score} / {module.questions.count()}")
    p.drawString(100, height - 160, f"Время: {progress.time_spent // 60}:{progress.time_spent % 60:02d}")
    p.drawString(100, height - 180, f"Дата: {progress.completed_at.strftime('%d.%m.%Y %H:%M')}")

    p.showPage()
    p.save()
    
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename=f"results_{module.slug}.pdf")

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
            is_question_correct = False
            
            if question.type == 'multiple_choice':
                choice_id = request.POST.get(f'question_{question.id}')
                if choice_id:
                    choice = get_object_or_404(Choice, id=choice_id)
                    is_question_correct = choice.is_correct
                    UserAnswer.objects.create(
                        user=request.user, question=question, choice=choice, is_correct=is_question_correct
                    )
            
            elif question.type == 'sorting':
                all_sorted_correct = True
                for choice in question.choices.all():
                    user_order = request.POST.get(f'sort_{question.id}_{choice.id}')
                    if user_order:
                        user_order = int(user_order)
                        correct = (user_order == choice.order)
                        if not correct: all_sorted_correct = False
                        UserAnswer.objects.create(
                            user=request.user, question=question, choice=choice, 
                            user_order=user_order, is_correct=correct
                        )
                is_question_correct = all_sorted_correct
            
            elif question.type == 'matching':
                all_matched_correct = True
                for choice in question.choices.all():
                    user_match = request.POST.get(f'match_{question.id}_{choice.id}')
                    correct = (user_match == choice.pair_text)
                    if not correct: all_matched_correct = False
                    UserAnswer.objects.create(
                        user=request.user, question=question, choice=choice,
                        matched_text=user_match, is_correct=correct
                    )
                is_question_correct = all_matched_correct
            
            elif question.type == 'text_input':
                user_text = request.POST.get(f'text_{question.id}', '').strip().lower()
                # Считаем верным, если совпадает с любым вариантом ответа, помеченным как верный
                correct_choices = question.choices.filter(is_correct=True)
                for choice in correct_choices:
                    if user_text == choice.text.strip().lower():
                        is_question_correct = True
                        break
                UserAnswer.objects.create(
                    user=request.user, question=question, user_input=user_text, is_correct=is_question_correct
                )

            if is_question_correct:
                score += 1
            else:
                errors_count += 1
        
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
    user_answers = UserAnswer.objects.filter(user=request.user, question__module=module).select_related('question', 'choice').prefetch_related('question__choices')
    
    # Группируем ответы по вопросам для правильного отображения в шаблоне
    grouped_answers = {}
    for ans in user_answers:
        if ans.question_id not in grouped_answers:
            grouped_answers[ans.question_id] = {
                'question': ans.question,
                'is_correct': True, # Будет обновлено ниже
                'answers': []
            }
        grouped_answers[ans.question_id]['answers'].append(ans)
        if not ans.is_correct:
            grouped_answers[ans.question_id]['is_correct'] = False

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
    
    # Сложность модуля
    module_difficulty = _("Средняя")
    if user_answers.exists():
        module_difficulty = user_answers.first().question.difficulty

    return render(request, 'courses/test_results.html', {
        'module': module,
        'progress': progress,
        'grouped_answers': grouped_answers.values(),
        'total_questions': total_questions,
        'score_percent': score_percent,
        'stroke_dashoffset': stroke_dashoffset,
        'time_formatted': time_formatted,
        'next_module': next_module,
        'module_difficulty': module_difficulty,
        'share_url': request.build_absolute_uri(reverse('courses:shared_results', args=[progress.share_token])),
    })

def shared_results_view(request, token):
    """Публичный просмотр результатов по токену (без логина)"""
    progress = get_object_or_404(UserProgress.objects.select_related('user', 'module'), share_token=token)
    module = progress.module
    user_answers = UserAnswer.objects.filter(user=progress.user, question__module=module).select_related('question', 'choice').prefetch_related('question__choices')
    
    grouped_answers = {}
    for ans in user_answers:
        if ans.question_id not in grouped_answers:
            grouped_answers[ans.question_id] = {
                'question': ans.question,
                'is_correct': True,
                'answers': []
            }
        grouped_answers[ans.question_id]['answers'].append(ans)
        if not ans.is_correct:
            grouped_answers[ans.question_id]['is_correct'] = False

    total_questions = module.questions.count()
    score_percent = int((progress.score / total_questions * 100)) if total_questions > 0 else 0
    stroke_dashoffset = 263.89 - (263.89 * score_percent / 100)
    
    mins = progress.time_spent // 60
    secs = progress.time_spent % 60
    time_formatted = f"{mins:02d}:{secs:02d}"

    return render(request, 'courses/test_results.html', {
        'module': module,
        'progress': progress,
        'grouped_answers': grouped_answers.values(),
        'total_questions': total_questions,
        'score_percent': score_percent,
        'stroke_dashoffset': stroke_dashoffset,
        'time_formatted': time_formatted,
        'is_shared_view': True,
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

