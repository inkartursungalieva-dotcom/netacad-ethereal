from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'accounts'

urlpatterns = [
    # Регистрация и вход
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('notifications/', views.notifications_view, name='notifications'),
    path('notifications/read/<int:pk>/', views.mark_notification_read_view, name='mark_notification_read'),
    path('change-language/', views.change_language_view, name='change_language'),
    
    # Подтверждение email
    path('verify-email/', views.verify_email_view, name='verify_email'),
    path('resend-verification/', views.resend_verification_view, name='resend_verification'),
    
    # Смена пароля
    path('password-change/', 
         auth_views.PasswordChangeView.as_view(
             template_name='accounts/password_change_form.html',
             success_url='/accounts/password-change/done/'
         ), 
         name='password_change'),
    path('password-change/done/', 
         auth_views.PasswordChangeDoneView.as_view(
             template_name='accounts/password_change_done.html'
         ), 
         name='password_change_done'),

    # 🔐 Сброс пароля — ВСЕ 4 обязательных URL
    path('password-reset/', 
         auth_views.PasswordResetView.as_view(
             template_name='accounts/password_reset_form.html',
             email_template_name='accounts/password_reset_email.html',
             subject_template_name='accounts/password_reset_subject.txt',
             success_url='/accounts/password-reset/done/'
         ), 
         name='password_reset'),
    
    path('password-reset/done/', 
         auth_views.PasswordResetDoneView.as_view(
             template_name='accounts/password_reset_done.html'
         ), 
         name='password_reset_done'),
    
    path('reset/<uidb64>/<token>/',  # 🔥 Ключевой путь для password_reset_confirm
         auth_views.PasswordResetConfirmView.as_view(
             template_name='accounts/password_reset_confirm.html',
             success_url='/accounts/reset/done/'
         ), 
         name='password_reset_confirm'),
    
    path('reset/done/', 
         auth_views.PasswordResetCompleteView.as_view(
             template_name='accounts/password_reset_complete.html'
         ), 
         name='password_reset_complete'),
]