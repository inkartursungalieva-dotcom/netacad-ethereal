#!/usr/bin/env python
"""
📧 Тест отправки email в Django
Запуск: python test_email.py
"""
import os
import sys
import django

# Добавляем проект в путь
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Настраиваем Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.core.mail import send_mail
from django.conf import settings

def test_email():
    """Отправка тестового письма"""
    
    recipient = input("📮 Введите email для теста: ").strip()
    if not recipient:
        recipient = 'inkartursungalieva@gmail.com'  # email по умолчанию
    
    print(f"\n📤 Отправка письма на: {recipient}")
    print(f"🔧 Бэкенд: {settings.EMAIL_BACKEND}\n")
    
    try:
        send_mail(
            subject='🔧 Тест email — NetAcad Ethereal',
            message='''
Здравствуйте!

Это тестовое письмо из вашего Django-проекта "NetAcad Ethereal".

Если вы видите это сообщение — настройка отправки email работает корректно! ✅

---
С уважением,
Команда разработки
            ''',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recipient],
            fail_silently=False,  # Показывать ошибки, если есть
        )
        print("✅ Письмо успешно отправлено!")
        
        if 'console' in settings.EMAIL_BACKEND:
            print("📋 Проверьте терминал — там должно быть содержимое письма.\n")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка отправки: {type(e).__name__}")
        print(f"📝 Детали: {e}\n")
        return False


if __name__ == '__main__':
    print("🚀 Запуск теста email...\n")
    success = test_email()
    sys.exit(0 if success else 1)