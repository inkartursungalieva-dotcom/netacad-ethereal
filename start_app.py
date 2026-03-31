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

def run_django():
    """Запуск Django сервера"""
    try:
        # Автоматическое применение миграций перед запуском
        print("🛠 Проверка базы данных...")
        execute_from_command_line([sys.argv[0], 'migrate', '--noinput'])
        
        # Создание суперпользователя по умолчанию, если нужно (необязательно)
        # execute_from_command_line([sys.argv[0], 'shell', '-c', "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username='admin').exists() or User.objects.create_superuser('admin', 'admin@example.com', 'admin')"])

        print("🚀 Запуск сервера NetAcad Ethereal...")
        execute_from_command_line([sys.argv[0], 'runserver', '127.0.0.1:8000', '--noreload'])
    except Exception as e:
        print(f"❌ Ошибка при запуске: {e}")
        input("Нажмите Enter, чтобы закрыть...")

if __name__ == "__main__":
    # Запуск открытия браузера в отдельном потоке
    threading.Thread(target=open_browser, daemon=True).start()
    
    # Запуск сервера
    run_django()
