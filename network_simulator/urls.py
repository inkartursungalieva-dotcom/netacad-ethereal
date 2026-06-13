from django.urls import path

from . import views

app_name = "network_simulator"

urlpatterns = [
    path("topology/", views.topology_api, name="topology"),
    path("topology/save/", views.topology_save_api, name="topology_save"),
    path("device/add/", views.device_add_api, name="device_add"),
    path("device/update/", views.device_update_api, name="device_update"),
    path("device/delete/", views.device_delete_api, name="device_delete"),
    path("connection/create/", views.connection_create_api, name="connection_create"),
    path("connection/delete/", views.connection_delete_api, name="connection_delete"),
    path("simulation/start/", views.simulation_start_api, name="simulation_start"),
    path("network/check/", views.network_check_api, name="network_check"),
    # VLAN endpoints
    path("vlan/list/", views.vlan_list_api, name="vlan_list"),
    path("vlan/create/", views.vlan_create_api, name="vlan_create"),
    path("vlan/delete/", views.vlan_delete_api, name="vlan_delete"),
    # DHCP endpoints
    path("dhcp/list/", views.dhcp_list_api, name="dhcp_list"),
    path("dhcp/create/", views.dhcp_create_api, name="dhcp_create"),
    path("dhcp/delete/", views.dhcp_delete_api, name="dhcp_delete"),
    # Terminal History endpoint
    path("terminal/history/add/", views.terminal_history_add_api, name="terminal_history_add"),
    # AI Helper endpoint
    path("ai/helper/", views.ai_helper_api, name="ai_helper"),
]
