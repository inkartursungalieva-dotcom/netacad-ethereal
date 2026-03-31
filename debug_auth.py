#!/usr/bin/env python
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model, authenticate

User = get_user_model()

print("🔍 Проверка пользователей в базе:\n")

users = User.objects.all()
for user in users:
    print(f"Username: {user.username}")
    print(f"Email: {user.email}")
    print(f"Is Active: {user.is_active}")
    print(f"Has password: {user.has_usable_password()}")
    print()
    
    # Попробуем аутентифицировать
    print("🔐 Тест аутентификации:")
    
    # По username
    auth_user = authenticate(username=user.username, password='test123456')
    print(f"  По username: {'✅' if auth_user else '❌'}")
    
    # По email (если email совпадает)
    try:
        user_by_email = User.objects.get(email=user.email)
        auth_by_email = authenticate(username=user_by_email.username, password='test123456')
        print(f"  По email: {'✅' if auth_by_email else '❌'}")
    except:
        print(f"  По email: ❌ (пользователь не найден)")
    
    print("-" * 50)