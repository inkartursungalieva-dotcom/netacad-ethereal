"""
Базовые тесты для моделей проекта.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from courses.models import Module, Question, Choice, UserProgress
from laboratory.models import Lab, LabProgress
from accounts.models import User

User = get_user_model()


class UserModelTest(TestCase):
    """Тесты модели User"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            role='student'
        )
    
    def test_user_creation(self):
        """Тест создания пользователя"""
        self.assertEqual(self.user.username, 'testuser')
        self.assertEqual(self.user.email, 'test@example.com')
        self.assertEqual(self.user.role, 'student')
        self.assertTrue(self.user.check_password('testpass123'))
    
    def test_user_str(self):
        """Тест строкового представления пользователя"""
        self.assertIn('testuser', str(self.user))
    
    def test_completed_onboarding_default(self):
        """Тест значения по умолчанию для completed_onboarding"""
        self.assertFalse(self.user.completed_onboarding)


class ModuleModelTest(TestCase):
    """Тесты модели Module"""
    
    def setUp(self):
        self.module = Module.objects.create(
            slug='test-module',
            name='Test Module',
            name_kk='Сынақ модуль',
            order=1,
            description='Test description'
        )
    
    def test_module_creation(self):
        """Тест создания модуля"""
        self.assertEqual(self.module.slug, 'test-module')
        self.assertEqual(self.module.name, 'Test Module')
        self.assertEqual(self.module.order, 1)
    
    def test_module_str(self):
        """Тест строкового представления модуля"""
        self.assertEqual(str(self.module), 'Test Module')
    
    def test_test_duration_minutes(self):
        """Тест расчёта времени теста"""
        # Без вопросов - минимум 5 минут
        self.assertEqual(self.module.test_duration_minutes, 5)
        
        # С вопросами
        question = Question.objects.create(
            module=self.module,
            text='Test question',
            difficulty='Easy',
            type='multiple_choice'
        )
        self.assertGreaterEqual(self.module.test_duration_minutes, 5)


class LabModelTest(TestCase):
    """Тесты модели Lab"""
    
    def setUp(self):
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
            category='basic',
            difficulty='easy',
            estimated_time=30
        )
    
    def test_lab_creation(self):
        """Тест создания лабораторной работы"""
        self.assertEqual(self.lab.title, 'Test Lab')
        self.assertEqual(self.lab.category, 'basic')
        self.assertEqual(self.lab.difficulty, 'easy')
        self.assertEqual(self.lab.estimated_time, 30)
    
    def test_lab_str(self):
        """Тест строкового представления лабораторной работы"""
        self.assertEqual(str(self.lab), 'Test Lab (Test Module)')
    
    def test_get_tags_list(self):
        """Тест получения списка тегов"""
        self.lab.tags = 'OSI, IP, Routing'
        self.lab.save()
        tags = self.lab.get_tags_list()
        self.assertEqual(tags, ['OSI', 'IP', 'Routing'])
    
    def test_get_tags_list_empty(self):
        """Тест получения списка тегов без тегов"""
        tags = self.lab.get_tags_list()
        self.assertEqual(tags, [])


class LabProgressModelTest(TestCase):
    """Тесты модели LabProgress"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
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
            scenario_data={'nodes': [], 'links': []}
        )
    
    def test_lab_progress_creation(self):
        """Тест создания прогресса лабораторной работы"""
        progress = LabProgress.objects.create(
            user=self.user,
            lab=self.lab,
            score=80,
            is_completed=True
        )
        self.assertEqual(progress.score, 80)
        self.assertTrue(progress.is_completed)
        self.assertEqual(progress.attempts, 1)  # attempts увеличивается при save
    
    def test_lab_progress_unique(self):
        """Тест уникальности прогресса для пользователя и лабы"""
        LabProgress.objects.create(
            user=self.user,
            lab=self.lab,
            score=50
        )
        # Попытка создать второй прогресс для той же пары user-lab
        with self.assertRaises(Exception):  # IntegrityError
            LabProgress.objects.create(
                user=self.user,
                lab=self.lab,
                score=70
            )
