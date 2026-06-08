from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from allauth.socialaccount.models import SocialApp
from django.contrib.sites.models import Site
from courses.models import Module, UserProgress

User = get_user_model()

class AuthTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.register_url = reverse('accounts:register')
        self.login_url = reverse('accounts:login')
        
        # Создаем Site и SocialApp для Google (нужно для рендеринга шаблонов с allauth)
        site = Site.objects.get_current()
        SocialApp.objects.create(
            provider='google',
            name='Google',
            client_id='test-client-id',
            secret='test-secret'
        ).sites.add(site)
        
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password1': 'StrongPassword123!',
            'password2': 'StrongPassword123!',
            'role': 'student',
            'language': 'ru',
            'terms': True
        }

    def test_registration_success(self):
        """Тест успешной регистрации и автоматического входа"""
        response = self.client.post(self.register_url, self.user_data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(email='test@example.com').exists())
        
        user = User.objects.get(email='test@example.com')
        self.assertTrue(user.email_verified)
        self.assertTrue(user.is_active)

    def test_login_success(self):
        """Тест успешного входа"""
        # Создаем пользователя
        user = User.objects.create_user(
            username='loginuser', 
            email='login@example.com', 
            password='StrongPassword123!',
            email_verified=True
        )
        
        response = self.client.post(self.login_url, {
            'username': 'login@example.com',
            'password': 'StrongPassword123!'
        })
        self.assertEqual(response.status_code, 302)

class ProgressTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='progressuser', 
            email='progress@example.com', 
            password='StrongPassword123!'
        )
        self.module = Module.objects.create(name='Test Module', slug='test-module', order=1)

    def test_course_progress_calculation(self):
        """Тест централизованного расчета прогресса"""
        # Начальный прогресс
        progress = self.user.get_course_progress()
        self.assertEqual(progress['progress_percent'], 0)
        
        # Завершаем модуль
        UserProgress.objects.create(user=self.user, module=self.module, is_completed=True, score=100)
        
        progress = self.user.get_course_progress()
        self.assertEqual(progress['progress_percent'], 100)
        self.assertEqual(progress['completed_count'], 1)
