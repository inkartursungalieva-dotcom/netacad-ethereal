import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.sites.models import Site

def fix_site():
    domain = os.getenv('PYTHONANYWHERE_DOMAIN', 'inkara.pythonanywhere.com') # Подставь свой домен
    site_id = 1
    
    try:
        site = Site.objects.get(id=site_id)
        site.domain = domain
        site.name = "NetAcad Ethereal"
        site.save()
        print(f"✅ Site ID {site_id} обновлен: {domain}")
    except Site.DoesNotExist:
        Site.objects.create(id=site_id, domain=domain, name="NetAcad Ethereal")
        print(f"✅ Site ID {site_id} создан: {domain}")

if __name__ == "__main__":
    fix_site()
