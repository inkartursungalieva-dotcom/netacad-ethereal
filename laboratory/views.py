from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.db import models
from .models import Lab, LabProgress
from courses.models import Module
import json

@login_required
def lab_list_view(request):
    """Список всех практических работ с фильтрацией (расширенный функционал)"""
    labs_queryset = Lab.objects.select_related('module').filter(is_active=True)
    
    # Фильтрация по категории
    category_filter = request.GET.get('category')
    if category_filter:
        labs_queryset = labs_queryset.filter(category=category_filter)
    
    # Фильтрация по сложности
    difficulty_filter = request.GET.get('difficulty')
    if difficulty_filter:
        labs_queryset = labs_queryset.filter(difficulty=difficulty_filter)
    
    # Фильтрация по тегам
    tag_filter = request.GET.get('tag')
    if tag_filter:
        labs_queryset = labs_queryset.filter(tags__icontains=tag_filter)
    
    labs = labs_queryset.order_by('order', 'module__order')
    
    # Оптимизированный загрузка прогресса пользователя (не для админов/преподавателей)
    if request.user.role == 'teacher' or request.user.is_superuser:
        user_progress = {}
    else:
        user_progress_data = LabProgress.objects.filter(
            user=request.user
        ).values('lab_id', 'is_completed', 'score', 'attempts', 'time_spent')
        
        user_progress = {p['lab_id']: p for p in user_progress_data}
    
    for lab in labs:
        progress_data = user_progress.get(lab.id)
        if progress_data:
            lab.progress = LabProgress(
                is_completed=progress_data['is_completed'],
                score=progress_data['score'],
                attempts=progress_data.get('attempts', 0),
                time_spent=progress_data.get('time_spent', 0)
            )
        else:
            lab.progress = None
    
    # Получаем уникальные категории и сложности для фильтров
    categories = Lab.objects.filter(is_active=True).values_list('category', flat=True).distinct()
    difficulties = Lab.objects.filter(is_active=True).values_list('difficulty', flat=True).distinct()
    
    return render(request, 'laboratory/lab_list.html', {
        'labs': labs,
        'current_category': category_filter,
        'current_difficulty': difficulty_filter,
        'current_tag': tag_filter,
        'categories': categories,
        'difficulties': difficulties,
    })

@login_required
def lab_detail_view(request, module_slug):
    """Страница конкретной практической работы (симулятор)"""
    module = get_object_or_404(Module, slug=module_slug)
    lab = Lab.objects.filter(module=module).first()
    if not lab:
        related = Module.objects.filter(order__lt=module.order).order_by('-order').first()
        return render(request, 'laboratory/lab_placeholder.html', {
            'module': module,
            'related_module': related,
        })
    # Если пользователь - преподаватель или админ, не создаем прогресс
    if request.user.role == 'teacher' or request.user.is_superuser:
        progress = None
    else:
        progress, created = LabProgress.objects.get_or_create(user=request.user, lab=lab)
    
    # Определяем шаблон в зависимости от типа лаборатории (по слагу)
    template_name = 'laboratory/lab_simulator.html'
    if module_slug == 'osi_model':
        template_name = 'laboratory/osi_lab.html'
    elif module_slug == 'lan':
        template_name = 'laboratory/office_lab.html'
    elif module_slug == 'tcp_ip':
        template_name = 'laboratory/tcp_lab.html'
    elif module_slug == 'ip_addressing':
        template_name = 'laboratory/ip_lab.html'
    elif module_slug == 'switching':
        template_name = 'laboratory/switching_lab.html'
    
    return render(request, template_name, {
        'lab': lab,
        'module': module,
        'progress': progress
    })

@login_required
def network_designer_view(request):
    """Отображение собственного сетевого конструктора (Network Designer)"""
    return render(request, 'laboratory/network_designer.html')

@login_required
def save_lab_progress(request, lab_id):
    """AJAX сохранение прогресса лаборатории с улучшенным отслеживанием"""
    if request.method == 'POST':
        data = json.loads(request.body)
        score = int(data.get('score', 0))
        completed = data.get('completed', False)
        history = data.get('history', [])
        time_spent = int(data.get('time_spent', 0))  # Время в секундах
        
        # Если пользователь - преподаватель или админ, не сохраняем результат
        if request.user.role == 'teacher' or request.user.is_superuser:
            return JsonResponse({
                'status': 'success',
                'attempts': 1,
                'time_spent': time_spent,
                'message': 'Результат не сохранен (вы администратор)'
            })
        
        # Серверная проверка (Important 15)
        # 1. Если баллы > 0, должна быть история команд
        if score > 0 and len(history) < 2:
            score = 0
            completed = False
        
        # 2. Базовая проверка сложности (минимум 5 команд для 100 баллов)
        if score == 100 and len(history) < 5:
            score = 50  # Снижаем балл за подозрительно быстрое выполнение
        
        lab = get_object_or_404(Lab, id=lab_id)
        progress, created = LabProgress.objects.get_or_create(user=request.user, lab=lab)
        
        progress.score = score
        progress.commands_history = history
        progress.time_spent = time_spent  # Сохраняем затраченное время
        
        if completed and not progress.is_completed:
            progress.is_completed = True
            progress.completed_at = timezone.now()
            
        progress.save()
        return JsonResponse({
            'status': 'success',
            'attempts': progress.attempts,
            'time_spent': progress.time_spent
        })
    
    return JsonResponse({'status': 'error'}, status=400)

@login_required
def lab_statistics_view(request):
    """Статистика лабораторных работ пользователя"""
    user_progress = LabProgress.objects.filter(user=request.user).select_related('lab', 'lab__module')
    
    total_labs = Lab.objects.filter(is_active=True).count()
    completed_labs = user_progress.filter(is_completed=True).count()
    total_score = user_progress.aggregate(total=models.Sum('score'))['total'] or 0
    total_time = user_progress.aggregate(time=models.Sum('time_spent'))['time'] or 0
    total_attempts = user_progress.aggregate(attempts=models.Sum('attempts'))['attempts'] or 0
    
    # Вычисляем минуты из секунд
    total_time_minutes = round(total_time / 60, 1) if total_time > 0 else 0
    
    # Статистика по категориям
    category_stats = {}
    for progress in user_progress:
        category = progress.lab.category
        if category not in category_stats:
            category_stats[category] = {'completed': 0, 'total': 0, 'avg_score': 0}
        category_stats[category]['total'] += 1
        if progress.is_completed:
            category_stats[category]['completed'] += 1
        category_stats[category]['avg_score'] += progress.score
    
    for category in category_stats:
        if category_stats[category]['total'] > 0:
            category_stats[category]['avg_score'] = round(
                category_stats[category]['avg_score'] / category_stats[category]['total'], 1
            )
    
    return render(request, 'laboratory/lab_statistics.html', {
        'user_progress': user_progress,
        'total_labs': total_labs,
        'completed_labs': completed_labs,
        'total_score': total_score,
        'total_time': total_time,
        'total_time_minutes': total_time_minutes,
        'total_attempts': total_attempts,
        'category_stats': category_stats,
    })
