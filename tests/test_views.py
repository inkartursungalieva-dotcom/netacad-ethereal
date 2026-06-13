"""
Базовые тесты для views проекта.
"""

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from courses.models import Module
from laboratory.models import Lab

User = get_user_model()


class HomeViewTest(TestCase):
    """Тесты для домашней страницы"""
    
    def test_home_page_status(self):
        """Тест статуса домашней страницы"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
    
    def test_home_page_template(self):
        """Тест шаблона домашней страницы"""
        response = self.client.get('/')
        self.assertTemplateUsed(response, 'home.html')


class LabListViewTest(TestCase):
    """Тесты для списка лабораторных работ"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')
        
        self.module = Module.objects.create(
            slug='test-module',
            name='Test Module',
            order=1,
            description='Test description'
        )
        self.lab = Lab.objects.create(
            module=self.module,
            title='Test Lab',
            description='Test lab description',
            scenario_data={'nodes': [], 'links': []},
            is_active=True
        )
    
    def test_lab_list_requires_login(self):
        """Тест того, что список лаб требует авторизации"""
        self.client.logout()
        response = self.client.get(reverse('laboratory:list'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_lab_list_authenticated(self):
        """Тест списка лаб для авторизованного пользователя"""
        response = self.client.get(reverse('laboratory:list'))
        self.assertEqual(response.status_code, 200)
    
    def test_lab_list_shows_active_labs(self):
        """Тест отображения только активных лаб"""
        self.lab.is_active = False
        self.lab.save()
        
        response = self.client.get(reverse('laboratory:list'))
        self.assertEqual(response.status_code, 200)
        # Лаборатория не должна отображаться в списке
        self.assertNotContains(response, 'Test Lab')


class LabStatisticsViewTest(TestCase):
    """Тесты для страницы статистики лабораторных работ"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')
    
    def test_statistics_requires_login(self):
        """Тест того, что статистика требует авторизации"""
        self.client.logout()
        response = self.client.get(reverse('laboratory:statistics'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_statistics_authenticated(self):
        """Тест страницы статистики для авторизованного пользователя"""
        response = self.client.get(reverse('laboratory:statistics'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'laboratory/lab_statistics.html')


class OnboardingViewsTest(TestCase):
    """Тесты для системы онбординга"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')
    
    def test_onboarding_welcome_requires_login(self):
        """Тест того, что онбординг требует авторизации"""
        self.client.logout()
        response = self.client.get('/onboarding/welcome/')
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_onboarding_welcome_authenticated(self):
        """Тест страницы приветствия онбординга"""
        response = self.client.get('/onboarding/welcome/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'onboarding/welcome.html')
    
    def test_onboarding_complete_sets_flag(self):
        """Тест установки флага completed_onboarding"""
        response = self.client.post('/onboarding/complete/')
        self.assertEqual(response.status_code, 200)
        
        self.user.refresh_from_db()
        self.assertTrue(self.user.completed_onboarding)
