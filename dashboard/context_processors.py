from accounts.models import Notification
from courses.models import Module, UserProgress

def dashboard_context(request):
    """Контекстный процессор для дашборда (уведомления, прогресс)"""
    if not request.user.is_authenticated:
        return {}
    
    progress = request.user.get_course_progress()
    modules = Module.objects.all().order_by('order')
    
    return {
        'sidebar_modules': modules,
        **progress
    }
