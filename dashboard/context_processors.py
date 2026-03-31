from accounts.models import Notification
from courses.models import Module, UserProgress

def dashboard_context(request):
    """Контекстный процессор для дашборда (уведомления, прогресс)"""
    if not request.user.is_authenticated:
        return {}
    
    # Количество непрочитанных уведомлений
    unread_notifications_count = Notification.objects.filter(user=request.user, is_read=False).count()
    
    # Базовый прогресс для сайдбара
    modules = Module.objects.all()
    user_progress = UserProgress.objects.filter(user=request.user)
    completed_modules = [p.module.id for p in user_progress if p.is_completed]
    
    completed_count = len(completed_modules)
    total_count = modules.count()
    progress_percent = int((completed_count / total_count * 100)) if total_count > 0 else 0
    
    return {
        'sidebar_modules': modules.order_by('order'),
        'unread_notifications_count': unread_notifications_count,
        'completed_count': completed_count,
        'total_count': total_count,
        'progress_percent': progress_percent,
    }
