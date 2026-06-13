from django.contrib import admin
from django.contrib.auth.views import LogoutView
from django.urls import path, include, re_path
from core import views as core_views
from django.shortcuts import render
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve

# Тестовые представления для страниц ошибок
def error_404_view(request, exception=None):
    return render(request, '404.html', status=404)

def error_500_view(request):
    return render(request, '500.html', status=500)

urlpatterns = [
    path('admin/logout/', LogoutView.as_view(next_page='home'), name='admin_logout'),
    path('admin/', admin.site.urls),
    path('i18n/', include('django.conf.urls.i18n')),
    path('', core_views.home_view, name='home'),
    path('about/', core_views.about_view, name='about'),
    path('api-docs/', core_views.api_docs_view, name='api_docs'),
    path('api/ai-chat/', core_views.ai_chat_api, name='ai_chat_api'),
    path('api/', include('network_simulator.urls')),
    path('legal/<str:page_type>/', core_views.legal_view, name='legal'),
    path('accounts/', include('accounts.urls')),  
    path('accounts/', include('allauth.urls')),  # Allauth URLs
    path('courses/', include('courses.urls')),  
    path('dashboard/', include('dashboard.urls')),  
    path('laboratory/', include('laboratory.urls')),
    # Onboarding URLs
    path('onboarding/welcome/', core_views.onboarding_welcome, name='onboarding_welcome'),
    path('onboarding/guide/', core_views.onboarding_guide, name='onboarding_guide'),
    path('onboarding/labs/', core_views.onboarding_labs, name='onboarding_labs'),
    path('onboarding/ai-assistant/', core_views.onboarding_ai_assistant, name='onboarding_ai_assistant'),
    path('onboarding/complete/', core_views.onboarding_complete, name='onboarding_complete'),
    path('onboarding/skip/', core_views.onboarding_skip, name='onboarding_skip'),
]

if settings.DEBUG:
    urlpatterns += [
        # Тестовые маршруты для проверки дизайна (только для отладки)
        path('test404/', error_404_view),
        path('test500/', error_500_view),
    ]
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
else:
    # WhiteNoise отдаёт STATIC; загрузки (аватары, файлы модулей) — через Django (Render и др.)
    urlpatterns += [
        re_path(
            r'^media/(?P<path>.*)$',
            serve,
            {'document_root': settings.MEDIA_ROOT},
        ),
    ]

# Глобальные обработчики ошибок для production (DEBUG=False)
handler404 = 'config.urls.error_404_view'
handler500 = 'config.urls.error_500_view'
