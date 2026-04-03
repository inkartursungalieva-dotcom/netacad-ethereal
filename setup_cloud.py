import os
import django
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.sites.models import Site
from django.contrib.auth import get_user_model
from allauth.socialaccount.models import SocialApp
from django.core.management import call_command

def setup():
    # 1. Применяем миграции
    print("Applying migrations...")
    call_command('migrate', no_input=True)

    # 2. Настраиваем Site ID
    print("Setting up Site ID...")
    domain = os.getenv('RENDER_EXTERNAL_HOSTNAME') or 'netacad-ethereal-inkar.onrender.com'
    site, _ = Site.objects.get_or_create(id=1, defaults={'domain': domain, 'name': 'NetAcad Ethereal'})
    site.domain = domain
    site.save()

    # 3. Наполняем контентом (только если модулей еще нет)
    from courses.models import Module
    if not Module.objects.exists():
        print("Filling database with content (takes ~30s)...")
        try:
            import init_db
            import add_labs
            import add_questions
            init_db.run()
            # Ускоряем запуск: добавляем только базу, остальное можно догрузить позже если надо
            # Но для защиты лучше иметь всё сразу
            add_labs.create_labs()
            add_questions.run()
        except Exception as e:
            print(f"Warning: Error filling database: {e}")
    else:
        print("Database already contains data, skipping.")

    # 4. Создаем дефолтного админа (для тестов на защите)
    User = get_user_model()
    if not User.objects.filter(is_superuser=True).exists():
        print("Creating superuser (admin/admin123)...")
        User.objects.create_superuser('admin', 'admin@example.com', 'admin123')

    # 5. Настройка Google OAuth (пустышка, чтобы Allauth не падал)
    if not SocialApp.objects.filter(provider='google').exists():
        print("Setting up Google OAuth placeholder...")
        app = SocialApp.objects.create(
            provider='google',
            name='Google',
            client_id='placeholder',
            secret='placeholder'
        )
        app.sites.add(site)

    print("Setup completed successfully!")

if __name__ == "__main__":
    setup()
