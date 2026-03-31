import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from laboratory.models import Lab

def add_hints_to_labs():
    lab_hints = {
        'introduction': 'Команды для выполнения:\n1. en - переход в привилегированный режим\n2. conf t - режим глобальной конфигурации\n3. hostname NetAcad_R1 - смена имени устройства',
        'osi_model': 'Подсказка:\nИспользуйте команду "ping [IP]" для проверки связности на сетевом уровне.\nИспользуйте "sh int" для просмотра физических параметров.',
        'tcp_ip': 'Команды:\n- show ip int brief: краткий статус интерфейсов\n- show protocols: просмотр активных протоколов',
        'ip_addressing': 'Пример настройки IP:\n(config)# interface g0/0\n(config-if)# ip address 192.168.1.1 255.255.255.0\n(config-if)# no shutdown',
        'protocols': 'Используйте "show service" для проверки статуса HTTP/DNS.\nДля запроса к DNS: "nslookup google.com"',
        'lan': 'Создание VLAN:\n(config)# vlan 10\n(config-vlan)# name IT_Dept\n(config-vlan)# exit',
        'switching': 'Настройка порта:\n(config)# interface fa0/1\n(config-if)# switchport mode access\n(config-if)# switchport access vlan 10',
        'routing': 'Статическая маршрутизация:\n(config)# ip route 192.168.2.0 255.255.255.0 10.0.0.1',
        'security': 'Настройка ACL:\n(config)# access-list 10 permit 192.168.1.0 0.0.0.255\n(config)# interface g0/0\n(config-if)# ip access-group 10 in',
        'wireless': 'Основные команды:\n- ssid NetAcad_Free\n- encryption wpa2 psk [password]',
        'cloud': 'Настройка туннеля:\n- interface tunnel 0\n- tunnel source g0/0\n- tunnel destination [remote_ip]',
        'client_server': 'Проверка подключения:\n- telnet 10.0.0.50 80 (HTTP)\n- ping 10.0.0.50 (Связность)'
    }

    for slug, hint in lab_hints.items():
        try:
            lab = Lab.objects.get(module__slug=slug)
            lab.hints = hint
            lab.save()
            print(f"Добавлены подсказки для модуля: {slug}")
        except Lab.DoesNotExist:
            print(f"Лабораторная для модуля {slug} не найдена.")

if __name__ == "__main__":
    add_hints_to_labs()
