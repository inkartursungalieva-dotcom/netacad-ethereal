import json

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_GET, require_POST

from .models import NetworkConnection, NetworkDevice, SimulationSession, VLAN, DHCPServer, PacketLog, TerminalHistory
from .services import (
    check_topology,
    default_interfaces,
    get_or_create_user_topology,
    run_simulation,
    serialize_device,
    serialize_topology,
)


def request_data(request):
    if request.content_type == "application/json":
        try:
            return json.loads(request.body or "{}")
        except json.JSONDecodeError:
            return {}
    return request.POST


@login_required
@require_GET
def topology_api(request):
    topology = get_or_create_user_topology(request.user)
    return JsonResponse(serialize_topology(topology))


@login_required
@require_POST
def topology_save_api(request):
    topology = get_or_create_user_topology(request.user)
    data = request_data(request)
    name = data.get("name", "").strip()
    if name:
        topology.name = name
    if data.get("submit"):
        topology.is_submitted = True
        topology.submitted_at = timezone.now()
    topology.save()
    return JsonResponse({"topology": serialize_topology(topology)})


@login_required
@require_POST
def device_add_api(request):
    topology = get_or_create_user_topology(request.user)
    data = request_data(request)
    device_type = data.get("type", "pc")
    count = topology.devices.filter(type=device_type).count() + 1
    name = data.get("name") or f"{device_type.upper()}{count}"
    device = NetworkDevice.objects.create(
        topology=topology,
        name=name,
        type=device_type,
        x=int(data.get("x", 160)),
        y=int(data.get("y", 160)),
        status=data.get("status", "active"),
        ip_address=data.get("ip_address") or "",
        subnet_mask=data.get("subnet_mask") or "",
        gateway=data.get("gateway") or "",
        dns=data.get("dns") or "",
        hostname=data.get("hostname") or name,
        interfaces=data.get("interfaces") or default_interfaces(device_type),
    )
    return JsonResponse({"device": serialize_device(device)}, status=201)


@login_required
@require_POST
def device_update_api(request):
    topology = get_or_create_user_topology(request.user)
    data = request_data(request)
    device = NetworkDevice.objects.get(id=data.get("id"), topology=topology)

    editable_fields = [
        "name",
        "type",
        "x",
        "y",
        "status",
        "ip_address",
        "subnet_mask",
        "gateway",
        "dns",
        "hostname",
        "interfaces",
        "routes",
    ]
    for field in editable_fields:
        if field in data:
            setattr(device, field, data[field])
    device.save()
    return JsonResponse({"device": serialize_device(device)})


@login_required
@require_POST
def connection_create_api(request):
    topology = get_or_create_user_topology(request.user)
    data = request_data(request)
    source = NetworkDevice.objects.get(id=data.get("source_device"), topology=topology)
    target = NetworkDevice.objects.get(id=data.get("target_device"), topology=topology)
    if source.id == target.id:
        return JsonResponse({"error": "Нельзя соединить устройство само с собой"}, status=400)

    connection, _ = NetworkConnection.objects.get_or_create(
        topology=topology,
        source_device=source,
        target_device=target,
        defaults={
            "cable_type": data.get("cable_type", "auto"),
            "status": data.get("status", "connected"),
        },
    )
    return JsonResponse(
        {
            "connection": {
                "id": connection.id,
                "source_device": connection.source_device_id,
                "target_device": connection.target_device_id,
                "cable_type": connection.cable_type,
                "status": connection.status,
            }
        },
        status=201,
    )


@login_required
@require_POST
def simulation_start_api(request):
    topology = get_or_create_user_topology(request.user)
    data = request_data(request)
    source = NetworkDevice.objects.get(id=data.get("source_device"), topology=topology)
    target = NetworkDevice.objects.get(id=data.get("target_device"), topology=topology)
    protocol = data.get("protocol", "icmp")

    result = run_simulation(topology, source, target)
    session = SimulationSession.objects.create(
        topology=topology,
        protocol=protocol,
        source_device=source,
        target_device=target,
        result=result,
        status=result["status"],
        completed_at=timezone.now(),
        packet_path=result["path"],
    )
    
    # Save packet log
    PacketLog.objects.create(
        simulation=session,
        source_device=source,
        target_device=target,
        route=result["path"],
        status=result["status"],
    )
    
    return JsonResponse({"session_id": session.id, "result": result})


@login_required
@require_POST
def device_delete_api(request):
    topology = get_or_create_user_topology(request.user)
    data = request_data(request)
    device = NetworkDevice.objects.get(id=data.get("id"), topology=topology)
    device.delete()
    return JsonResponse({"success": True})


@login_required
@require_POST
def connection_delete_api(request):
    topology = get_or_create_user_topology(request.user)
    data = request_data(request)
    connection = NetworkConnection.objects.get(id=data.get("id"), topology=topology)
    connection.delete()
    return JsonResponse({"success": True})


@login_required
@require_POST
def network_check_api(request):
    topology = get_or_create_user_topology(request.user)
    data = request_data(request)
    result = check_topology(topology, data.get("source_device"), data.get("target_device"))
    return JsonResponse(result)


# VLAN API endpoints
@login_required
@require_GET
def vlan_list_api(request):
    topology = get_or_create_user_topology(request.user)
    vlans = [{"id": v.id, "vlan_id": v.vlan_id, "name": v.name, "color": v.color} for v in topology.vlans.all()]
    return JsonResponse({"vlans": vlans})


@login_required
@require_POST
def vlan_create_api(request):
    topology = get_or_create_user_topology(request.user)
    data = request_data(request)
    vlan = VLAN.objects.create(
        topology=topology,
        vlan_id=data.get("vlan_id"),
        name=data.get("name"),
        color=data.get("color", "#9b59b6"),
    )
    return JsonResponse({"vlan": {"id": vlan.id, "vlan_id": vlan.vlan_id, "name": vlan.name, "color": vlan.color}}, status=201)


@login_required
@require_POST
def vlan_delete_api(request):
    topology = get_or_create_user_topology(request.user)
    data = request_data(request)
    vlan = VLAN.objects.get(id=data.get("id"), topology=topology)
    vlan.delete()
    return JsonResponse({"success": True})


# DHCP API endpoints
@login_required
@require_GET
def dhcp_list_api(request):
    topology = get_or_create_user_topology(request.user)
    dhcp_servers = []
    for server in topology.dhcp_servers.select_related("device"):
        dhcp_servers.append({
            "id": server.id,
            "device_id": server.device.id,
            "device_name": server.device.name,
            "start_ip": server.start_ip,
            "end_ip": server.end_ip,
            "subnet_mask": server.subnet_mask,
            "gateway": server.gateway,
            "dns": server.dns,
            "lease_time": server.lease_time,
        })
    return JsonResponse({"dhcp_servers": dhcp_servers})


@login_required
@require_POST
def dhcp_create_api(request):
    topology = get_or_create_user_topology(request.user)
    data = request_data(request)
    device = NetworkDevice.objects.get(id=data.get("device_id"), topology=topology)
    dhcp_server = DHCPServer.objects.create(
        topology=topology,
        device=device,
        start_ip=data.get("start_ip"),
        end_ip=data.get("end_ip"),
        subnet_mask=data.get("subnet_mask", "255.255.255.0"),
        gateway=data.get("gateway"),
        dns=data.get("dns"),
        lease_time=data.get("lease_time", 86400),
    )
    return JsonResponse({
        "dhcp_server": {
            "id": dhcp_server.id,
            "device_id": dhcp_server.device.id,
            "start_ip": dhcp_server.start_ip,
            "end_ip": dhcp_server.end_ip,
            "subnet_mask": dhcp_server.subnet_mask,
            "gateway": dhcp_server.gateway,
            "dns": dhcp_server.dns,
            "lease_time": dhcp_server.lease_time,
        }
    }, status=201)


@login_required
@require_POST
def dhcp_delete_api(request):
    topology = get_or_create_user_topology(request.user)
    data = request_data(request)
    dhcp_server = DHCPServer.objects.get(id=data.get("id"), topology=topology)
    dhcp_server.delete()
    return JsonResponse({"success": True})


# Terminal History API endpoint
@login_required
@require_POST
def terminal_history_add_api(request):
    topology = get_or_create_user_topology(request.user)
    data = request_data(request)
    device = NetworkDevice.objects.get(id=data.get("device_id"), topology=topology)
    terminal_history = TerminalHistory.objects.create(
        device=device,
        command=data.get("command"),
        output=data.get("output"),
    )
    return JsonResponse({"id": terminal_history.id, "command": terminal_history.command, "output": terminal_history.output}, status=201)


# AI Helper API endpoint (placeholder)
@login_required
@require_POST
def ai_helper_api(request):
    topology = get_or_create_user_topology(request.user)
    data = request_data(request)
    prompt = data.get("prompt", "")
    
    # Simple AI helper (can be extended with real API)
    response = "AI helper is not configured yet. Please add your API key in settings."
    
    return JsonResponse({"response": response})

