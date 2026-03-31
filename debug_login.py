#!/usr/bin/env python
import os, sys, django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import authenticate, get_user_model
User = get_user_model()

email = input("📧 Email: ").strip()
password = input("🔑 Пароль: ").strip()

print(f"\n🔍 Поиск пользователя по email: {email}")
try:
    user = User.objects.get(email__iexact=email)
    print(f"✅ Найден: username={user.username}, active={user.is_active}")
    
    print("\n🔐 Проверка пароля...")
    auth_user = authenticate(username=user.username, password=password)
    if auth_user:
        print("✅ Аутентификация успешна!")
    else:
        print("❌ Неверный пароль")
        # Проверим, хеширован ли пароль
        print(f"   check_password: {user.check_password(password)}")
except User.DoesNotExist:
    print("❌ Пользователь не найден")