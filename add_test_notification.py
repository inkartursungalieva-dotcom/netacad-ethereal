import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from accounts.models import User, Notification

def add_test_notifications():
    users = User.objects.all()
    if not users.exists():
        print("Пользователи не найдены. Создайте пользователя через register или manage.py createsuperuser.")
        return

    for user in users:
        Notification.objects.create(
            user=user,
            title="Добро пожаловать!",
            message="Вы успешно активировали систему уведомлений. Теперь вы будете получать важные сообщения здесь.",
            is_read=False
        )
        print(f"Добавлено уведомление для {user.username}")

if __name__ == "__main__":
    add_test_notifications()
