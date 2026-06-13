from django.db import models
from django.conf import settings
import json


class NetworkTopology(models.Model):
    """Модель для хранения сетевой топологии"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='network_topologies',
        null=True,
        blank=True
    )
    name = models.CharField(max_length=255, verbose_name='Название топологии')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    is_submitted = models.BooleanField(default=False, verbose_name='Отправлено преподавателю')
    submitted_at = models.DateTimeField(null=True, blank=True, verbose_name='Дата отправки')

    class Meta:
        verbose_name = 'Сетевая топология'
        verbose_name_plural = 'Сетевые топологии'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.user})"


class NetworkDevice(models.Model):
    """Модель для сетевых устройств"""
    DEVICE_TYPES = [
        ('router', 'Router'),
        ('switch', 'Switch'),
        ('hub', 'Hub'),
        ('pc', 'PC'),
        ('server', 'Server'),
    ]

    topology = models.ForeignKey(
        NetworkTopology,
        on_delete=models.CASCADE,
        related_name='devices',
        verbose_name='Топология'
    )
    name = models.CharField(max_length=100, verbose_name='Имя устройства')
    type = models.CharField(
        max_length=20,
        choices=DEVICE_TYPES,
        verbose_name='Тип устройства'
    )
    x = models.IntegerField(default=0, verbose_name='Позиция X')
    y = models.IntegerField(default=0, verbose_name='Позиция Y')
    status = models.CharField(
        max_length=20,
        default='active',
        verbose_name='Статус'
    )
    
    # Сетевые настройки
    ip_address = models.CharField(
        max_length=45,
        blank=True,
        null=True,
        verbose_name='IP-адрес'
    )
    subnet_mask = models.CharField(
        max_length=45,
        blank=True,
        null=True,
        verbose_name='Маска подсети'
    )
    gateway = models.CharField(
        max_length=45,
        blank=True,
        null=True,
        verbose_name='Шлюз'
    )
    dns = models.CharField(
        max_length=45,
        blank=True,
        null=True,
        verbose_name='DNS'
    )
    hostname = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Hostname'
    )
    
    # Интерфейсы устройства (хранятся как JSON)
    interfaces = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='Интерфейсы'
    )
    
    # Маршруты (хранятся как JSON)
    routes = models.JSONField(
        default=list,
        blank=True,
        verbose_name='Маршруты'
    )

    class Meta:
        verbose_name = 'Сетевое устройство'
        verbose_name_plural = 'Сетевые устройства'
        ordering = ['id']

    def __str__(self):
        return f"{self.name} ({self.type})"


class NetworkConnection(models.Model):
    """Модель для соединений между устройствами"""
    CABLE_TYPES = [
        ('auto', 'Auto'),
        ('straight', 'Straight Through'),
        ('crossover', 'Cross Over'),
        ('fiber', 'Fiber'),
    ]

    topology = models.ForeignKey(
        NetworkTopology,
        on_delete=models.CASCADE,
        related_name='connections',
        verbose_name='Топология'
    )
    source_device = models.ForeignKey(
        NetworkDevice,
        on_delete=models.CASCADE,
        related_name='outgoing_connections',
        verbose_name='Исходное устройство'
    )
    target_device = models.ForeignKey(
        NetworkDevice,
        on_delete=models.CASCADE,
        related_name='incoming_connections',
        verbose_name='Целевое устройство'
    )
    cable_type = models.CharField(
        max_length=20,
        choices=CABLE_TYPES,
        default='auto',
        verbose_name='Тип кабеля'
    )
    status = models.CharField(
        max_length=20,
        default='connected',
        verbose_name='Статус'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    class Meta:
        verbose_name = 'Сетевое соединение'
        verbose_name_plural = 'Сетевые соединения'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.source_device.name} -> {self.target_device.name} ({self.cable_type})"


class SimulationSession(models.Model):
    """Модель для сессий симуляции"""
    PROTOCOLS = [
        ('icmp', 'ICMP (Ping)'),
    ]

    topology = models.ForeignKey(
        NetworkTopology,
        on_delete=models.CASCADE,
        related_name='simulations',
        verbose_name='Топология'
    )
    protocol = models.CharField(
        max_length=20,
        choices=PROTOCOLS,
        default='icmp',
        verbose_name='Протокол'
    )
    source_device = models.ForeignKey(
        NetworkDevice,
        on_delete=models.CASCADE,
        related_name='sent_simulations',
        null=True,
        blank=True,
        verbose_name='Исходное устройство'
    )
    target_device = models.ForeignKey(
        NetworkDevice,
        on_delete=models.CASCADE,
        related_name='received_simulations',
        null=True,
        blank=True,
        verbose_name='Целевое устройство'
    )
    started_at = models.DateTimeField(auto_now_add=True, verbose_name='Время начала')
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Время завершения'
    )
    result = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='Результат симуляции'
    )
    status = models.CharField(
        max_length=20,
        default='running',
        verbose_name='Статус'
    )
    
    # Путь пакета (хранится как список ID устройств)
    packet_path = models.JSONField(
        default=list,
        blank=True,
        verbose_name='Путь пакета'
    )

    class Meta:
        verbose_name = 'Сессия симуляции'
        verbose_name_plural = 'Сессии симуляции'
        ordering = ['-started_at']

    def __str__(self):
        return f"Simulation {self.id} - {self.protocol} ({self.status})"


class VLAN(models.Model):
    """Модель для VLAN"""
    VLAN_COLORS = [
        ('#9b59b6', 'Фиолетовый'),
        ('#3498db', 'Синий'),
        ('#2ecc71', 'Зеленый'),
        ('#e74c3c', 'Красный'),
        ('#f1c40f', 'Желтый'),
        ('#e67e22', 'Оранжевый'),
    ]

    topology = models.ForeignKey(
        NetworkTopology,
        on_delete=models.CASCADE,
        related_name='vlans',
        verbose_name='Топология'
    )
    vlan_id = models.IntegerField(verbose_name='VLAN ID')
    name = models.CharField(max_length=100, verbose_name='Название VLAN')
    color = models.CharField(
        max_length=20,
        choices=VLAN_COLORS,
        default='#9b59b6',
        verbose_name='Цвет'
    )

    class Meta:
        verbose_name = 'VLAN'
        verbose_name_plural = 'VLAN'
        unique_together = ('topology', 'vlan_id')
        ordering = ['vlan_id']

    def __str__(self):
        return f"VLAN {self.vlan_id} - {self.name}"


class DHCPServer(models.Model):
    """Модель для DHCP-сервера"""
    topology = models.ForeignKey(
        NetworkTopology,
        on_delete=models.CASCADE,
        related_name='dhcp_servers',
        verbose_name='Топология'
    )
    device = models.OneToOneField(
        NetworkDevice,
        on_delete=models.CASCADE,
        related_name='dhcp_server',
        verbose_name='Устройство'
    )
    start_ip = models.CharField(max_length=45, verbose_name='Начальный IP')
    end_ip = models.CharField(max_length=45, verbose_name='Конечный IP')
    subnet_mask = models.CharField(
        max_length=45,
        default='255.255.255.0',
        verbose_name='Маска подсети'
    )
    gateway = models.CharField(
        max_length=45,
        blank=True,
        null=True,
        verbose_name='Шлюз'
    )
    dns = models.CharField(
        max_length=45,
        blank=True,
        null=True,
        verbose_name='DNS'
    )
    lease_time = models.IntegerField(
        default=86400,
        verbose_name='Время аренды (сек)'
    )

    class Meta:
        verbose_name = 'DHCP-сервер'
        verbose_name_plural = 'DHCP-серверы'
        ordering = ['id']

    def __str__(self):
        return f"DHCP {self.device.name}"


class PacketLog(models.Model):
    """Модель для логирования симуляций"""
    simulation = models.ForeignKey(
        SimulationSession,
        on_delete=models.CASCADE,
        related_name='packets',
        verbose_name='Сессия симуляции'
    )
    source_device = models.ForeignKey(
        NetworkDevice,
        on_delete=models.CASCADE,
        related_name='sent_packets',
        verbose_name='Источник'
    )
    target_device = models.ForeignKey(
        NetworkDevice,
        on_delete=models.CASCADE,
        related_name='received_packets',
        verbose_name='Назначение'
    )
    route = models.JSONField(default=list, verbose_name='Маршрут')
    status = models.CharField(
        max_length=20,
        choices=[('success', 'Успешно'), ('error', 'Ошибка'), ('pending', 'В обработке')],
        default='pending',
        verbose_name='Статус'
    )
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name='Время')

    class Meta:
        verbose_name = 'Лог пакетов'
        verbose_name_plural = 'Логи пакетов'
        ordering = ['-timestamp']

    def __str__(self):
        return f"Packet {self.id} - {self.status}"


class TerminalHistory(models.Model):
    """Модель для истории команд терминала"""
    device = models.ForeignKey(
        NetworkDevice,
        on_delete=models.CASCADE,
        related_name='terminal_history',
        verbose_name='Устройство'
    )
    command = models.TextField(verbose_name='Команда')
    output = models.TextField(verbose_name='Вывод')
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name='Время')

    class Meta:
        verbose_name = 'История терминала'
        verbose_name_plural = 'История терминала'
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.device.name}: {self.command[:50]}"
