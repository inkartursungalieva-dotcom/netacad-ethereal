#!/usr/bin/env python
"""
🔐 Тест SMTP-подключения к Gmail
Запуск: python test_smtp.py
"""
import os
import sys
import django
import smtplib

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.conf import settings

def test_smtp_connection():
    """Проверка подключения к SMTP Gmail"""
    
    print("🔍 Проверка настроек...")
    print(f"   Host: {settings.EMAIL_HOST}")
    print(f"   Port: {settings.EMAIL_PORT}")
    print(f"   TLS: {settings.EMAIL_USE_TLS}")
    print(f"   User: {settings.EMAIL_HOST_USER}")
    print(f"   Password length: {len(settings.EMAIL_HOST_PASSWORD)} символов")
    print()
    
    try:
        print("🔌 Подключение к smtp.gmail.com:587...")
        server = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT)
        server.set_debuglevel(1)  # Показывать детали обмена
        
        print("🔐 Запуск TLS...")
        server.starttls()
        
        print("🔑 Аутентификация...")
        server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
        
        print("✅ Успешно! Подключение и вход выполнены.")
        server.quit()
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        print(f"\n❌ Ошибка аутентификации: {e}")
        print("\n💡 Возможные причины:")
        print("   1. Используете обычный пароль вместо App Password")
        print("   2. Не включена двухфакторная аутентификация")
        print("   3. В пароле есть пробелы (нужно удалить)")
        print("   4. Неверный email в EMAIL_HOST_USER")
        return False
        
    except Exception as e:
        print(f"\n❌ Ошибка: {type(e).__name__}: {e}")
        return False

if __name__ == '__main__':
    print("🚀 Тест SMTP подключения к Gmail\n")
    success = test_smtp_connection()
    sys.exit(0 if success else 1)