import os
import django
import json

# Настройка окружения Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from courses.models import Module
from laboratory.models import Lab

def create_labs():
    # Данные для практических работ (симуляций)
    labs_data = [
        {
            'slug': 'introduction',
            'title': 'Настройка Hostname',
            'description': 'Для изменения имени устройства используется команда <i>hostname ИМЯ</i> в режиме конфигурации.<br><br>Подключитесь к консоли маршрутизатора и измените его имя на "NetAcad_R1".',
            'scenario': {
                'devices': [
                    {'name': 'Router_0', 'type': 'router', 'x': 50, 'y': 50}
                ],
                'target_hostname': 'NetAcad_R1'
            }
        },
        {
            'slug': 'osi_model',
            'title': 'Анализ уровней OSI',
            'description': 'Команда <i>show interfaces</i> выводит детальную информацию о состоянии портов.<br><br>Проанализируйте состояние физического и канального уровней (L1/L2) интерфейса GigabitEthernet0/0.',
            'scenario': {
                'devices': [
                    {'name': 'Switch_0', 'type': 'switch', 'x': 50, 'y': 50}
                ]
            }
        },
        {
            'slug': 'tcp_ip',
            'title': '3-стороннее рукопожатие TCP',
            'description': 'Поймите фундаментальный процесс установления соединения TCP. Изучите, как Client и Server обмениваются пакетами SYN, SYN-ACK и ACK.',
            'scenario': {}
        },
        {
            'slug': 'ip_addressing',
            'title': 'Настройка IPv4 адреса',
            'description': 'Для настройки IP используйте:<br><i>interface Gi0/0</i><br><i>ip address 192.168.1.1 255.255.255.0</i><br><br>Настройте указанный IP-адрес на интерфейсе Gi0/0 маршрутизатора.',
            'scenario': {
                'devices': [
                    {'name': 'Router_ISP', 'type': 'router', 'x': 40, 'y': 40},
                    {'name': 'PC_Admin', 'type': 'pc', 'x': 60, 'y': 60}
                ]
            }
        },
        {
            'slug': 'lan',
            'title': 'Сборка офисной сети',
            'description': 'Соберите функциональную топологию для небольшого офиса. Убедитесь, что в сети есть сервер и минимум 3 устройства для базовой работы офиса.',
            'scenario': {
                'required_devices': 3,
                'required_types': ['server']
            }
        },
        {
            'slug': 'switching',
            'title': 'Таблица MAC-адресов',
            'description': 'Команда <i>show mac address-table</i> показывает, какие устройства подключены к портам коммутатора.<br><br>Найдите порт, к которому подключен PC_1.',
            'scenario': {
                'devices': [
                    {'name': 'Core_Switch', 'type': 'switch', 'x': 50, 'y': 50},
                    {'name': 'PC_1', 'type': 'pc', 'x': 30, 'y': 70},
                    {'name': 'PC_2', 'type': 'pc', 'x': 70, 'y': 70}
                ]
            }
        },
        {
            'slug': 'routing',
            'title': 'Статическая маршрутизация',
            'description': '<i>ip route 10.0.0.0 255.255.255.0 192.168.1.2</i> — направляет трафик в сеть 10.0.0.0 через соседний роутер.<br><br>Добавьте статический маршрут в сеть 10.0.0.0/24 через шлюз 192.168.1.2.',
            'scenario': {
                'devices': [
                    {'name': 'R1', 'type': 'router', 'x': 30, 'y': 50},
                    {'name': 'R2', 'type': 'router', 'x': 70, 'y': 50}
                ]
            }
        }
    ]

    for data in labs_data:
        try:
            module = Module.objects.get(slug=data['slug'])
            lab, created = Lab.objects.get_or_create(
                module=module,
                defaults={
                    'title': data['title'],
                    'description': data['description'],
                    'scenario_data': data['scenario']
                }
            )
            if created:
                print(f"Создана практика для модуля: {module.name}")
            else:
                lab.title = data['title']
                lab.description = data['description']
                lab.scenario_data = data['scenario']
                lab.save()
                print(f"Обновлена практика для модуля: {module.name}")
        except Module.DoesNotExist:
            print(f"Модуль со слагом {data['slug']} не найден. Пропуск.")

if __name__ == '__main__':
    create_labs()