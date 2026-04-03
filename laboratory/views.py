from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from .models import Lab, LabProgress
from courses.models import Module
import json

@login_required
def lab_list_view(request):
    """Список всех практических работ"""
    labs = Lab.objects.select_related('module').all().order_by('module__order')
    user_progress = {p.lab_id: p for p in LabProgress.objects.filter(user=request.user)}
    
    for lab in labs:
        lab.progress = user_progress.get(lab.id)
        
    return render(request, 'laboratory/lab_list.html', {'labs': labs})

@login_required
def lab_detail_view(request, module_slug):
    """Страница конкретной практической работы (симулятор)"""
    module = get_object_or_404(Module, slug=module_slug)
    lab = get_object_or_404(Lab, module=module)
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
def save_lab_progress(request, lab_id):
    """AJAX сохранение прогресса лаборатории"""
    if request.method == 'POST':
        lab = get_object_or_404(Lab, id=lab_id)
        data = json.loads(request.body)
        
        progress, created = LabProgress.objects.get_or_create(user=request.user, lab=lab)
        
        progress.score = data.get('score', progress.score)
        progress.commands_history = data.get('history', progress.commands_history)
        
        if data.get('completed', False) and not progress.is_completed:
            progress.is_completed = True
            progress.completed_at = timezone.now()
            
        progress.save()
        return JsonResponse({'status': 'success'})
    
    return JsonResponse({'status': 'error'}, status=400)
