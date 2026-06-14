import os
import django
from urllib.parse import urlparse

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

    # 2. Настраиваем Site ID (для allauth, абсолютных ссылок в письмах)
    print("Setting up Site ID...")
    domain = os.getenv('SITE_DOMAIN', '').strip()
    if not domain:
        ext_url = os.getenv('RENDER_EXTERNAL_URL', '').strip()
        if ext_url:
            # Убираем протокол и завершающий слэш
            domain = ext_url.replace('https://', '').replace('http://', '').rstrip('/')
    
    if not domain:
        domain = os.getenv('RENDER_EXTERNAL_HOSTNAME', '').strip()
    
    if not domain:
        # Пробуем вытащить из ALLOWED_HOSTS если там что-то кроме '*'
        allowed = os.getenv('ALLOWED_HOSTS', '')
        if allowed and '*' not in allowed:
            domain = allowed.split(',')[0].strip()

    if not domain:
        domain = 'netacad-ethereal-inkar-au9p.onrender.com'
    
    print(f"DEBUG: Using domain for Site: {domain}")
    site, _ = Site.objects.get_or_create(id=1, defaults={'domain': domain, 'name': 'Computer Networks'})
    site.domain = domain
    site.name = 'Computer Networks'
    site.save()

    # 3. Наполняем контентом (только если модулей еще нет)
    from courses.models import Module
    if not Module.objects.exists():
        print("Filling database with content...")
        try:
            import init_db
            import add_labs
            import add_questions
            # Используем ускоренную инициализацию для облака
            init_db.run()
            add_labs.create_labs()
            # add_questions.run() # Можно пропустить или запустить асинхронно если их слишком много
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

    # 5. Настройка Google OAuth
    google_client_id = os.getenv('GOOGLE_CLIENT_ID', '').strip()
    google_client_secret = os.getenv('GOOGLE_CLIENT_SECRET', '').strip()

    print(f"DEBUG: GOOGLE_CLIENT_ID value: {google_client_id[:10]}...")
    
    # ПРОВЕРКА: Не является ли ID хэшем коммита?
    if google_client_id and len(google_client_id) >= 40 and all(c in '0123456789abcdef' for c in google_client_id[:40]):
        print("❌ [ERROR] GOOGLE_CLIENT_ID looks like a GIT COMMIT HASH!")
        print("Please check your Render Environment Variables. You likely pasted the commit hash into GOOGLE_CLIENT_ID.")
        google_client_id = None

    if google_client_id and not google_client_id.endswith('.apps.googleusercontent.com'):
        print(f"❌ [ERROR] GOOGLE_CLIENT_ID is INVALID! It must end with '.apps.googleusercontent.com'")
        print(f"Current value: {google_client_id}")
        google_client_id = None 

    if google_client_id and google_client_secret:
        print(f"Setting up real Google OAuth credentials for {domain}...")
        app, created = SocialApp.objects.get_or_create(
            provider='google',
            defaults={
                'name': 'Google',
                'client_id': google_client_id,
                'secret': google_client_secret
            }
        )
        # Всегда обновляем, чтобы синхронизировать с переменными окружения
        app.client_id = google_client_id
        app.secret = google_client_secret
        app.save()
        
        # Привязываем ко всем сайтам (обычно только к одному, но для надежности)
        for s in Site.objects.all():
            app.sites.add(s)
            
        print(f"✅ SocialApp updated successfully for client_id: {google_client_id[:15]}...")
    else:
        print("⚠️ [WARNING] Skipping Google OAuth setup: real credentials not found or invalid.")
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
