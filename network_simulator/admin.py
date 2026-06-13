from django.contrib import admin
from .models import NetworkTopology, NetworkDevice, NetworkConnection, SimulationSession


@admin.register(NetworkTopology)
class NetworkTopologyAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'is_submitted', 'submitted_at', 'created_at', 'updated_at']
    list_filter = ['is_submitted', 'created_at', 'submitted_at']
    search_fields = ['name', 'user__email']


@admin.register(NetworkDevice)
class NetworkDeviceAdmin(admin.ModelAdmin):
    list_display = ['name', 'type', 'topology', 'ip_address', 'status']
    list_filter = ['type', 'status', 'topology']
    search_fields = ['name', 'ip_address', 'hostname']


@admin.register(NetworkConnection)
class NetworkConnectionAdmin(admin.ModelAdmin):
    list_display = ['source_device', 'target_device', 'cable_type', 'status', 'created_at']
    list_filter = ['cable_type', 'status', 'topology']


@admin.register(SimulationSession)
class SimulationSessionAdmin(admin.ModelAdmin):
    list_display = ['id', 'protocol', 'source_device', 'target_device', 'status', 'started_at']
    list_filter = ['protocol', 'status', 'topology']
    readonly_fields = ['started_at', 'completed_at', 'packet_path', 'result']
