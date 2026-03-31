import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from courses.models import Module, Question, Choice

def run():
    # Создание модулей
    modules_data = [
        {'name': 'Введение', 'slug': 'introduction', 'order': 1, 'description': 'Основы сетевых технологий, терминология и история развития сетей.'},
        {'name': 'Модель OSI', 'slug': 'osi_model', 'order': 2, 'description': 'Детальный разбор семи уровней взаимодействия сетевых систем.'},
        {'name': 'Стек TCP/IP', 'slug': 'tcp_ip', 'order': 3, 'description': 'Протоколы стека TCP/IP, их функции и сравнение с моделью OSI.'},
        {'name': 'IP-адресация', 'slug': 'ip_addressing', 'order': 4, 'description': 'IPv4, IPv6, маски подсетей и основы планирования адресного пространства.'},
        {'name': 'Протоколы', 'slug': 'protocols', 'order': 5, 'description': 'TCP/UDP, HTTP, DNS, DHCP и другие протоколы прикладного уровня.'},
        {'name': 'Локальные сети', 'slug': 'lan', 'order': 6, 'description': 'Ethernet, коммутаторы, VLAN и проектирование офисных сетей.'},
        {'name': 'Коммутация', 'slug': 'switching', 'order': 7, 'description': 'Принципы работы коммутаторов, таблицы MAC-адресов и STP.'},
        {'name': 'Маршрутизация', 'slug': 'routing', 'order': 8, 'description': 'Основы маршрутизации, статические и динамические маршруты, RIP, OSPF.'},
        {'name': 'Безопасность', 'slug': 'security', 'order': 9, 'description': 'Брандмауэры, ACL, шифрование и защита сетевой инфраструктуры.'},
        {'name': 'Беспроводные сети', 'slug': 'wireless', 'order': 10, 'description': 'Wi-Fi, Bluetooth, стандарты 802.11 и безопасность WLAN.'},
        {'name': 'Облачные технологии', 'slug': 'cloud', 'order': 11, 'description': 'Облачные вычисления, модели SaaS, PaaS, IaaS и виртуализация.'},
        {'name': 'Клиент-сервер', 'slug': 'client_server', 'order': 12, 'description': 'Архитектура распределенных систем и работа серверных служб.'},
        {'name': 'Итоговый проект', 'slug': 'final_project', 'order': 13, 'description': 'Развертывание виртуальной лаборатории и проектирование сети предприятия.'},
    ]

    for data in modules_data:
        module, created = Module.objects.get_or_create(slug=data['slug'], defaults=data)
        if not created:
            module.name = data['name']
            module.order = data['order']
            module.description = data['description']
            module.save()

    # Добавление вопросов для Модели OSI (как пример)
    osi_module = Module.objects.get(slug='osi_model')
    q1, _ = Question.objects.get_or_create(
        module=osi_module,
        text='Какой уровень модели OSI отвечает за логическую адресацию и маршрутизацию в сети?',
        defaults={'hint': 'Подумайте об IP-адресах и маршрутизаторах.', 'difficulty': 'Intermediate', 'category': 'Conceptual Analysis'}
    )
    Choice.objects.get_or_create(question=q1, text='Канальный уровень (Data Link)', defaults={'is_correct': False})
    Choice.objects.get_or_create(question=q1, text='Сетевой уровень (Network)', defaults={'is_correct': True})
    Choice.objects.get_or_create(question=q1, text='Транспортный уровень (Transport)', defaults={'is_correct': False})
    Choice.objects.get_or_create(question=q1, text='Физический уровень (Physical)', defaults={'is_correct': False})

    # Добавление вопросов для Введения (чтобы можно было начать)
    intro_module = Module.objects.get(slug='introduction')
    q2, _ = Question.objects.get_or_create(
        module=intro_module,
        text='Что такое компьютерная сеть?',
        defaults={'hint': 'Базовое определение.', 'difficulty': 'Easy', 'category': 'Basics'}
    )
    Choice.objects.get_or_create(question=q2, text='Группа соединенных компьютеров для обмена данными', defaults={'is_correct': True})
    Choice.objects.get_or_create(question=q2, text='Один мощный компьютер', defaults={'is_correct': False})
    Choice.objects.get_or_create(question=q2, text='Программа для чата', defaults={'is_correct': False})

    print("База данных успешно инициализирована модулями и тестовыми вопросами.")

if __name__ == '__main__':
    run()
