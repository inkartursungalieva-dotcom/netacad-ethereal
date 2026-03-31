from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_index, name='index'),
    path('teacher/', views.teacher_dashboard_index, name='teacher_index'),
    path('teacher/export-report/', views.export_report, name='export_report'),
    path('teacher/students/', views.students_list, name='students_list'),
    path('teacher/students/<int:user_id>/', views.student_detail, name='student_detail'),
    path('teacher/modules/create/', views.create_module, name='create_module'),
    path('teacher/modules/<int:module_id>/edit/', views.edit_module, name='edit_module'),
    path('teacher/modules/<int:module_id>/reset/', views.reset_module_view, name='reset_module'),
    path('teacher/modules/<int:module_id>/delete/', views.delete_module, name='delete_module'),
    path('teacher/mail/', views.mail_students, name='mail_students'),
    path('test-results/', views.test_results_list, name='test_results_list'),
    path('grades/', views.grades_view, name='grades'),
    path('support/', views.support_view, name='support'),
]
