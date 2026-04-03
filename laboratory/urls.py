from django.urls import path
from . import views

app_name = 'laboratory'

urlpatterns = [
    path('', views.lab_list_view, name='list'),
    path('<slug:module_slug>/', views.lab_detail_view, name='simulator'),
    path('save/<int:lab_id>/', views.save_lab_progress, name='save_progress'),
]