from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Lab, LabProgress
import json

@login_required
def lab_simulator_view(request, slug):
    lab = get_object_or_404(Lab, module__slug=slug)
    progress, created = LabProgress.objects.get_or_create(user=request.user, lab=lab)
    return render(request, 'laboratory/lab_simulator.html', {
        'lab': lab,
        'progress': progress,
    })

@login_required
def lab_submit_view(request, slug):
    if request.method == 'POST':
        lab = get_object_or_404(Lab, module__slug=slug)
        progress, created = LabProgress.objects.get_or_create(user=request.user, lab=lab)
        
        data = json.loads(request.body)
        progress.score = data.get('score', 0)
        progress.commands_history = data.get('history', [])
        progress.is_completed = True
        progress.save()
        
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)
