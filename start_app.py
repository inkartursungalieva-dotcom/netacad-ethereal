import os
import sys
import webbrowser
import time
import threading
from django.core.management import execute_from_command_line

# Установка переменой окружения для Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

def open_browser():
    """Открывает браузер через 3 секунды после запуска сервера"""
    time.sleep(3)
    url = "http://127.0.0.1:8000"
    print(f"🌍 Открываем браузер: {url}")
    webbrowser.open(url)

def fix_site_domain():
    """Исправляет домен сайта в базе данных для корректной работы ссылок локально"""
    try:
        from django.contrib.sites.models import Site
        site = Site.objects.get_or_create(id=1)[0]
        site.domain = "127.0.0.1:8000"
        site.name = "NetAcad Ethereal (Local)"
        site.save()
        print("✅ Домен сайта настроен на 127.0.0.1:8000")
    except Exception as e:
        print(f"⚠️ Не удалось обновить домен сайта: {e}")

def run_django():
    """Запуск Django сервера"""
    try:
        # Автоматическое применение миграций перед запуском
        print("🛠 Проверка базы данных...")
        execute_from_command_line([sys.argv[0], 'migrate', '--noinput'])
        
        # Исправляем домен сайта для Allauth и ссылок
        fix_site_domain()

        print("🚀 Запуск сервера NetAcad Ethereal...")
        print("💡 Если вы видите ошибку 'отказано в подключении', убедитесь, что порт 8000 не занят.")
        # Используем 0.0.0.0 чтобы работало и через localhost и через 127.0.0.1
        execute_from_command_line([sys.argv[0], 'runserver', '0.0.0.0:8000', '--noreload'])
    except Exception as e:
        print(f"❌ Ошибка при запуске: {e}")
        print("\nВозможные причины:")
        print("1. Порт 8000 уже занят другой программой.")
        print("2. База данных MySQL не запущена (если используется MySQL).")
        print("3. Ошибка в коде (см. текст выше).")
        input("\nНажмите Enter, чтобы закрыть...")

if __name__ == "__main__":
    # Запуск открытия браузера в отдельном потоке
    threading.Thread(target=open_browser, daemon=True).start()
    
    # Запуск сервера
    run_django()
