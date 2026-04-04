from django.urls import path
from . import views

app_name = 'laboratory'

urlpatterns = [
    path('', views.lab_list_view, name='list'),
    # Должен быть выше <slug:>, иначе «save» воспринимается как slug модуля и AJAX не работает
    path('save/<int:lab_id>/', views.save_lab_progress, name='save_progress'),
    path('<slug:module_slug>/', views.lab_detail_view, name='simulator'),
]