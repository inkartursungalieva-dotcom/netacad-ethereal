#!/usr/bin/env python
"""
🔐 Скрипт для исправления паролей пользователей
Запуск: python fix_passwords.py
"""
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

def fix_user_passwords():
    """Устанавливает корректно хешированные пароли"""
    
    # 🔧 Настройте здесь пользователей и пароли
    users_data = {
        'inkara': 'inkartursungalieva@gmail.com',  # username: desired_password
        'admin': 'Admin123!',
        'Sara': 'Sara123!',
        'inkar': 'Inkar123!',
    }
    
    print("🔐 Исправление паролей пользователей...\n")
    
    for username, password in users_data.items():
        try:
            user = User.objects.get(username=username)
            
            # set_password() правильно хеширует пароль
            user.set_password(password)
            user.save()
            
            print(f"✅ {username:15} | {user.email:30} | пароль обновлён")
            
        except User.DoesNotExist:
            print(f"⚠️  {username:15} | пользователь не найден")
        except Exception as e:
            print(f"❌ {username:15} | ошибка: {e}")
    
    print("\n🎉 Готово! Проверьте вход на сайте.")


def create_test_user():
    """Создаёт тестового пользователя для проверки"""
    email = 'test@netacad.com'
    username = 'testuser'
    password = 'Test123456!'
    
    if User.objects.filter(username=username).exists():
        print(f"ℹ️  Пользователь {username} уже существует")
        return
    
    user = User.objects.create_user(
        username=username,
        email=email,
        password=password,
        role='student',
        is_active=True
    )
    print(f"✅ Создан тестовый пользователь: {username} / {password}")


if __name__ == '__main__':
    fix_user_passwords()
    print()
    create_test_user()