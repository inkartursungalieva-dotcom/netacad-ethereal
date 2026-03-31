from django.urls import path
from . import views

app_name = 'courses'

urlpatterns = [
    path('roadmap/', views.roadmap_view, name='roadmap'),
    path('', views.course_list, name='list'),
    
    # path('introduction/', views.introduction_view, name='introduction'),
    # path('osi-model/', views.osi_model_view, name='osi_model'),
    # path('ip-addressing/', views.ip_addressing_view, name='ip_addressing'),
    # path('protocols/', views.protocols_view, name='protocols'),
    # path('lan/', views.lan_view, name='lan'),
    # path('security/', views.security_view, name='security'),
    # path('client-server/', views.client_server_view, name='client_server'),
    # path('final-project/', views.final_project_view, name='final_project'),
    
    # Тесты модулей
    path('test/<str:slug>/', views.module_test_view, name='module_test'),
    path('test/<str:slug>/results/', views.test_results_view, name='test_results'),

    # Учебные ресурсы
    path('resources/', views.resource_list_view, name='resource_list'),
    path('resources/add/', views.add_resource_view, name='add_resource'),
    path('resources/delete/<int:pk>/', views.delete_resource_view, name='delete_resource'),

    # Универсальный маршрут для модулей (должен быть в конце)
    path('<str:slug>/', views.module_detail_view, name='module_detail'),
]