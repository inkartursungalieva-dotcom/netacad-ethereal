from django.urls import path, re_path
from . import views

app_name = 'laboratory'

urlpatterns = [
    path('', views.lab_list_view, name='list'),
    path('statistics/', views.lab_statistics_view, name='statistics'),
    # Должен быть выше <slug:>, иначе «save» воспринимается как slug модуля и AJAX не работает
    path('save/<int:lab_id>/', views.save_lab_progress, name='save_progress'),
    path('designer/', views.network_designer_view, name='designer'),
    re_path(r'^(?P<module_slug>[-a-zA-Z0-9_а-яёА-ЯЁ]+)/$', views.lab_detail_view, name='simulator'),
]