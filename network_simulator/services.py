from collections import deque
from ipaddress import ip_address, ip_network


def serialize_device(device):
    return {
        "id": device.id,
        "name": device.name,
        "type": device.type,
        "x": device.x,
        "y": device.y,
        "status": device.status,
        "interfaces": device.interfaces or {},
        "ip_address": device.ip_address or "",
        "subnet_mask": device.subnet_mask or "",
        "gateway": device.gateway or "",
        "dns": device.dns or "",
        "hostname": device.hostname or device.name,
        "routes": device.routes or [],
    }


def serialize_connection(connection):
    return {
        "id": connection.id,
        "source_device": connection.source_device_id,
        "target_device": connection.target_device_id,
        "cable_type": connection.cable_type,
        "status": connection.status,
    }


def serialize_topology(topology):
    return {
        "id": topology.id,
        "name": topology.name,
        "is_submitted": topology.is_submitted,
        "submitted_at": topology.submitted_at.isoformat() if topology.submitted_at else None,
        "created_at": topology.created_at.isoformat(),
        "devices": [serialize_device(device) for device in topology.devices.all()],
        "connections": [
            serialize_connection(connection)
            for connection in topology.connections.select_related("source_device", "target_device")
        ],
    }


def default_interfaces(device_type):
    if device_type == "router":
        return {
            "GigabitEthernet0/0": {"status": "up", "ip_address": "", "subnet_mask": ""},
            "GigabitEthernet0/1": {"status": "up", "ip_address": "", "subnet_mask": ""},
        }
    if device_type in {"switch", "hub"}:
        return {
            "FastEthernet0/1": {"status": "up"},
            "FastEthernet0/2": {"status": "up"},
            "FastEthernet0/3": {"status": "up"},
            "FastEthernet0/4": {"status": "up"},
        }
    if device_type == "firewall":
        return {
            "GigabitEthernet0/0": {"status": "up", "ip_address": "", "subnet_mask": ""},
            "GigabitEthernet0/1": {"status": "up", "ip_address": "", "subnet_mask": ""},
        }
    if device_type == "ap":
        return {
            "FastEthernet0": {"status": "up", "ip_address": "", "subnet_mask": ""},
            "WiFi0": {"status": "up"},
        }
    return {"FastEthernet0": {"status": "up", "ip_address": "", "subnet_mask": ""}}


def get_or_create_user_topology(user):
    from .models import NetworkTopology

    owner = user if user.is_authenticated else None
    topology = NetworkTopology.objects.filter(user=owner).order_by("-updated_at", "-created_at").first()
    if not topology:
        topology = NetworkTopology.objects.create(user=owner, name="Учебная топология")
    return topology


def validate_ip_config(device):
    errors = []
    if device.type in {"pc", "server", "router"}:
        if not device.ip_address:
            errors.append("нет IP")
        else:
            try:
                ip_address(device.ip_address)
            except ValueError:
                errors.append("IP некорректен")

        if not device.subnet_mask:
            errors.append("нет маски")
        else:
            try:
                ip_network(f"0.0.0.0/{device.subnet_mask}")
            except ValueError:
                errors.append("неверная маска")

    if device.gateway:
        try:
            ip_address(device.gateway)
        except ValueError:
            errors.append("шлюз некорректен")
    
    # Check device status
    if device.status == "down":
        errors.append("устройство выключено")
    
    # Check interface statuses
    for iface_name, iface in (device.interfaces or {}).items():
        if iface.get("status") == "down":
            errors.append(f"{iface_name}: интерфейс выключен")
    
    return errors


def build_graph(topology):
    graph = {device.id: set() for device in topology.devices.all() if device.status != "down"}
    for connection in topology.connections.filter(status="connected"):
        # Check if both devices are up
        if connection.source_device.status == "down" or connection.target_device.status == "down":
            continue
        
        # Check if any interface is down
        # For simplicity, assume if device is up, interfaces are up
        graph.setdefault(connection.source_device_id, set()).add(connection.target_device_id)
        graph.setdefault(connection.target_device_id, set()).add(connection.source_device_id)
    return graph


def find_path(topology, source_id, target_id):
    graph = build_graph(topology)
    if source_id not in graph or target_id not in graph:
        return []

    queue = deque([(source_id, [source_id])])
    visited = {source_id}
    while queue:
        current, path = queue.popleft()
        if current == target_id:
            return path
        for neighbor in graph.get(current, set()):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, path + [neighbor]))
    return []


def same_subnet(device, other):
    if not device.ip_address or not device.subnet_mask or not other.ip_address:
        return False
    try:
        network = ip_network(f"{device.ip_address}/{device.subnet_mask}", strict=False)
        return ip_address(other.ip_address) in network
    except ValueError:
        return False


def gateway_exists(source, devices):
    if not source.gateway:
        return same_subnet(source, devices_by_ip(devices).get(source.ip_address, source))
    return any(device.ip_address == source.gateway for device in devices)


def devices_by_ip(devices):
    return {device.ip_address: device for device in devices if device.ip_address}


def check_topology(topology, source_id=None, target_id=None):
    devices = list(topology.devices.all())
    issues = []
    ok = []

    if not devices:
        issues.append({"type": "topology", "message": "нет устройств"})
        return {"success": False, "ok": ok, "issues": issues, "path": []}

    graph = build_graph(topology)
    disconnected = [device.name for device in devices if device.status != "down" and not graph.get(device.id)]
    if disconnected:
        for name in disconnected:
            issues.append({"type": "connection", "message": f"{name}: нет соединения"})
    else:
        ok.append("устройства подключены")

    for device in devices:
        for error in validate_ip_config(device):
            issues.append({"type": "ip", "device_id": device.id, "message": f"{device.name}: {error}"})
    if not any(issue["type"] == "ip" for issue in issues):
        ok.append("IP корректны")

    for device in devices:
        if device.type in {"pc", "server"} and device.gateway:
            if not any(candidate.ip_address == device.gateway for candidate in devices):
                issues.append({"type": "gateway", "device_id": device.id, "message": f"{device.name}: шлюз недоступен"})
    if not any(issue["type"] == "gateway" for issue in issues):
        ok.append("шлюз существует")

    path = []
    if source_id and target_id:
        path = find_path(topology, int(source_id), int(target_id))
        if not issues:
            if path:
                ok.append("маршрут найден")
            else:
                issues.append({"type": "route", "message": "маршрут не найден"})

    return {"success": not issues, "ok": ok, "issues": issues, "path": path}


def run_simulation(topology, source, target):
    validation = check_topology(topology, source.id, target.id)
    path = validation["path"]
    devices = {device.id: device for device in topology.devices.all()}
    hops = []

    if path:
        for index, device_id in enumerate(path):
            device = devices[device_id]
            hops.append(
                {
                    "device_id": device.id,
                    "name": device.name,
                    "type": device.type,
                    "state": "success" if validation["success"] else "error",
                    "order": index,
                }
            )

    return {
        "success": validation["success"] and bool(path),
        "status": "success" if validation["success"] and path else "error",
        "path": path,
        "hops": hops,
        "checks": validation,
        "message": "Пакет доставлен" if validation["success"] and path else "Пакет остановлен из-за ошибки",
    }
