import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from courses.models import Resource

def check_resources():
    resources = Resource.objects.all()
    print(f"Total resources: {resources.count()}")
    for res in resources:
        print(f"ID: {res.id}, Title: {res.title}, Type: {res.resource_type}, File: {res.file.name}")

if __name__ == "__main__":
    check_resources()
