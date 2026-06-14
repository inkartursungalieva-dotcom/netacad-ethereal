(function () {
  const root = document.querySelector(".netlab");
  if (!root) return;

  function getTrans(key, defaultVal) {
    return (window.NetlabTranslations && window.NetlabTranslations[key]) || defaultVal;
  }

  const csrf = root.dataset.csrf;
  const state = {
    topology: null,
    devices: [],
    connections: [],
    selectedCable: "auto",
    pendingSource: null,
    modalDevice: null,
    originalDeviceData: null,
    terminalMode: "exec",
    terminalInterface: null,
    simulationHistory: [],
  };

  const canvas = document.getElementById("canvas");
  const linksLayer = document.getElementById("linksLayer");
  const packet = document.getElementById("packet");
  const emptyState = document.getElementById("emptyState");
  const deviceList = document.getElementById("deviceList");
  const sourceSelect = document.getElementById("sourceSelect");
  const targetSelect = document.getElementById("targetSelect");
  const protocolSelect = document.getElementById("protocolSelect");
  const checkList = document.getElementById("checkList");
  const eventLog = document.getElementById("eventLog");
  const modePill = document.getElementById("modePill");

  const modal = document.getElementById("deviceModal");
  const helpModal = document.getElementById("helpModal");
  const terminalOutput = document.getElementById("terminalOutput");
  const terminalInput = document.getElementById("terminalInput");
  const terminalPrompt = document.getElementById("terminalPrompt");

  function api(url, data) {
    const options = data === undefined
      ? { headers: { "Accept": "application/json" } }
      : {
          method: "POST",
          headers: {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "X-CSRFToken": csrf,
          },
          body: JSON.stringify(data),
        };
    return fetch(url, options).then((response) => {
      if (!response.ok) {
        return response.json().catch(() => ({})).then((body) => {
          throw new Error(body.error || getTrans("apiError", "Ошибка API"));
        });
      }
      return response.json();
    });
  }

  function iconFor(type) {
    return { router: "R", switch: "SW", hub: "H", pc: "PC", server: "SRV", firewall: "FW", ap: "AP" }[type] || "NET";
  }

  function deviceLabel(device) {
    return `${device.name}${device.ip_address ? " (" + device.ip_address + ")" : ""}`;
  }

  function byId(id) {
    return state.devices.find((device) => Number(device.id) === Number(id));
  }

  function connectionById(id) {
    return state.connections.find((connection) => Number(connection.id) === Number(id));
  }

  function linkKey(a, b) {
    return [Number(a), Number(b)].sort((x, y) => x - y).join("-");
  }

  function hasChanges() {
    if (!state.modalDevice || !state.originalDeviceData) return false;
    const device = state.modalDevice;
    const original = state.originalDeviceData;
    const currentIp = document.getElementById("deviceIp").value;
    const currentMask = document.getElementById("deviceMask").value;
    const currentGateway = document.getElementById("deviceGateway").value;
    const currentDns = document.getElementById("deviceDns").value;
    const currentHostname = document.getElementById("deviceHostname").value;
    const currentStatus = document.getElementById("deviceStatus").value;
    const currentRoutes = document.getElementById("routesInput").value;

    return (
      currentIp !== (original.ip_address || "") ||
      currentMask !== (original.subnet_mask || "") ||
      currentGateway !== (original.gateway || "") ||
      currentDns !== (original.dns || "") ||
      currentHostname !== (original.hostname || original.name || "") ||
      currentStatus !== (original.status || "active") ||
      currentRoutes !== JSON.stringify(original.routes || [], null, 2)
    );
  }

  function render() {
    canvas.querySelectorAll(".node").forEach((node) => node.remove());
    linksLayer.innerHTML = "";
    emptyState.style.display = state.devices.length ? "none" : "grid";

    state.connections.forEach((connection) => {
      const source = byId(connection.source_device);
      const target = byId(connection.target_device);
      if (!source || !target) return;
      const line = document.createElementNS("http://www.w3.org/2000/svg", "line");
      line.classList.add("link");
      line.dataset.key = linkKey(source.id, target.id);
      line.dataset.id = connection.id;
      line.setAttribute("x1", source.x);
      line.setAttribute("y1", source.y);
      line.setAttribute("x2", target.x);
      line.setAttribute("y2", target.y);
      line.style.cursor = "pointer";
      line.addEventListener("click", () => deleteConnection(connection.id));
      linksLayer.appendChild(line);
    });

    state.devices.forEach((device) => {
      const node = document.createElement("button");
      node.className = "node";
      node.type = "button";
      node.dataset.id = device.id;
      node.dataset.type = device.type;
      node.dataset.status = device.status;
      node.style.left = `${device.x}px`;
      node.style.top = `${device.y}px`;
      node.innerHTML = `
        <span class="node__status"></span>
        <span class="node__icon">${iconFor(device.type)}</span>
        <span class="node__name">${escapeHtml(device.name)}</span>
        <span class="node__ip">${escapeHtml(device.ip_address || getTrans("ipNotSet", "IP не задан"))}</span>
      `;
      node.addEventListener("mousedown", startDrag);
      node.addEventListener("click", () => selectForConnection(device.id));
      node.addEventListener("dblclick", () => openDevice(device));
      canvas.appendChild(node);
    });

    renderSidebars();
  }

  function renderSidebars() {
    const options = state.devices.map((device) => `<option value="${device.id}">${escapeHtml(deviceLabel(device))}</option>`).join("");
    sourceSelect.innerHTML = options;
    targetSelect.innerHTML = options;
    if (state.devices[0]) sourceSelect.value = state.devices[0].id;
    if (state.devices[1]) targetSelect.value = state.devices[1].id;

    deviceList.innerHTML = state.devices.length
      ? state.devices.map((device) => `
          <button class="list-row" type="button" data-open="${device.id}" style="grid-template-columns: 1fr auto; gap: 8px;">
            <div style="display: grid; gap: 3px;">
              <b>${escapeHtml(device.name)}</b>
              <span>${escapeHtml(device.type)} · ${escapeHtml(device.ip_address || getTrans("noIp", "нет IP"))}</span>
            </div>
            <button type="button" class="netlab-btn netlab-btn--ghost" data-delete="${device.id}" style="padding: 6px 10px; font-size: 11px;">${getTrans("delete", "Удалить")}</button>
          </button>
        `).join("")
      : `<p class="muted">${getTrans("noDevices", "Устройств пока нет.")}</p>`;

    deviceList.querySelectorAll("[data-open]").forEach((row) => {
      row.addEventListener("click", (e) => {
        if (e.target.dataset.delete) return;
        openDevice(byId(row.dataset.open));
      });
    });
    deviceList.querySelectorAll("[data-delete]").forEach((btn) => {
      btn.addEventListener("click", (e) => {
        e.stopPropagation();
        deleteDevice(Number(btn.dataset.delete));
      });
    });

    // Render connections list
    const connectionList = document.getElementById("connectionList");
    connectionList.innerHTML = state.connections.length
      ? state.connections.map((connection) => {
        const source = byId(connection.source_device);
        const target = byId(connection.target_device);
        if (!source || !target) return "";
        return `
          <div class="list-row" style="grid-template-columns: 1fr auto; gap: 8px;">
            <div style="display: grid; gap: 3px;">
              <b>${escapeHtml(source.name)} ↔ ${escapeHtml(target.name)}</b>
              <span>${escapeHtml(labelCable(connection.cable_type))}</span>
            </div>
            <button type="button" class="netlab-btn netlab-btn--ghost" data-delete-connection="${connection.id}" style="padding: 6px 10px; font-size: 11px;">${getTrans("delete", "Удалить")}</button>
          </div>
        `;
      }).join("")
      : `<p class="muted">${getTrans("noDevices", "Соединений пока нет.")}</p>`;

    connectionList.querySelectorAll("[data-delete-connection]").forEach((btn) => {
      btn.addEventListener("click", () => {
        deleteConnection(Number(btn.dataset.deleteConnection));
      });
    });
  }

  function startDrag(event) {
    const node = event.currentTarget;
    const device = byId(node.dataset.id);
    const rect = canvas.getBoundingClientRect();
    const startX = event.clientX;
    const startY = event.clientY;
    const originalX = device.x;
    const originalY = device.y;

    function move(moveEvent) {
      device.x = Math.max(46, Math.min(rect.width - 46, originalX + moveEvent.clientX - startX));
      device.y = Math.max(46, Math.min(rect.height - 46, originalY + moveEvent.clientY - startY));
      node.style.left = `${device.x}px`;
      node.style.top = `${device.y}px`;
      redrawLinksOnly();
    }

    function stop() {
      document.removeEventListener("mousemove", move);
      document.removeEventListener("mouseup", stop);
      api("/api/device/update/", { id: device.id, x: Math.round(device.x), y: Math.round(device.y) }).catch(showError);
    }

    document.addEventListener("mousemove", move);
    document.addEventListener("mouseup", stop);
  }

  function redrawLinksOnly() {
    linksLayer.querySelectorAll(".link").forEach((line) => {
      const [a, b] = line.dataset.key.split("-");
      const source = byId(a);
      const target = byId(b);
      if (!source || !target) return;
      line.setAttribute("x1", source.x);
      line.setAttribute("y1", source.y);
      line.setAttribute("x2", target.x);
      line.setAttribute("y2", target.y);
    });
  }

  function selectForConnection(deviceId) {
    if (!state.pendingSource) {
      state.pendingSource = deviceId;
      highlightNode(deviceId);
      modePill.textContent = getTrans("selectSecondDevice", "Выберите второе устройство");
      return;
    }
    if (Number(state.pendingSource) === Number(deviceId)) return;

    api("/api/connection/create/", {
      source_device: state.pendingSource,
      target_device: deviceId,
      cable_type: state.selectedCable,
    }).then((data) => {
      state.connections.push(data.connection);
      state.pendingSource = null;
      modePill.textContent = `${getTrans("cableLabel", "Кабель")}: ${labelCable(state.selectedCable)}`;
      render();
    }).catch(showError);
  }

  function highlightNode(deviceId) {
    canvas.querySelectorAll(".node").forEach((node) => {
      node.classList.toggle("is-selected", Number(node.dataset.id) === Number(deviceId));
    });
  }

  function openDevice(device) {
    if (!device) return;
    state.modalDevice = device;
    state.originalDeviceData = JSON.parse(JSON.stringify(device));
    state.terminalMode = "exec";
    state.terminalInterface = null;

    document.getElementById("modalType").textContent = device.type;
    document.getElementById("modalTitle").textContent = device.name;
    document.getElementById("deviceIp").value = device.ip_address || "";
    document.getElementById("deviceMask").value = device.subnet_mask || "";
    document.getElementById("deviceGateway").value = device.gateway || "";
    document.getElementById("deviceDns").value = device.dns || "";
    document.getElementById("deviceHostname").value = device.hostname || device.name;
    document.getElementById("deviceStatus").value = device.status || "active";
    document.getElementById("routesInput").value = JSON.stringify(device.routes || [], null, 2);
    renderInterfaces(device);
    terminalOutput.textContent = `${device.hostname || device.name}> `;
    updatePrompt();
    showModal(modal);
  }

  function renderInterfaces(device) {
    const list = document.getElementById("interfacesList");
    const entries = Object.entries(device.interfaces || {});
    list.innerHTML = entries.length
      ? entries.map(([name, data]) => `
          <div class="interface-row">
            <div><b>${escapeHtml(name)}</b><br><span>${escapeHtml(data.ip_address || "no ip")} · ${escapeHtml(data.status || "down")}</span></div>
            <span>${data.status === "up" ? "✓ up" : "down"}</span>
          </div>
        `).join("")
      : `<p class="muted">${getTrans("interfacesNotConfigured", "Интерфейсы не настроены.")}</p>`;
  }

  function saveModalDevice() {
    const device = state.modalDevice;
    let routes = [];
    try {
      routes = JSON.parse(document.getElementById("routesInput").value || "[]");
    } catch (error) {
      showError(new Error(getTrans("routesMustBeJson", "Маршруты должны быть JSON-массивом")));
      return;
    }

    api("/api/device/update/", {
      id: device.id,
      ip_address: document.getElementById("deviceIp").value.trim(),
      subnet_mask: document.getElementById("deviceMask").value.trim(),
      gateway: document.getElementById("deviceGateway").value.trim(),
      dns: document.getElementById("deviceDns").value.trim(),
      hostname: document.getElementById("deviceHostname").value.trim(),
      name: document.getElementById("deviceHostname").value.trim() || device.name,
      status: document.getElementById("deviceStatus").value,
      routes,
    }).then((data) => {
      Object.assign(device, data.device);
      state.originalDeviceData = JSON.parse(JSON.stringify(data.device));
      hideModal(modal);
      render();
    }).catch(showError);
  }

  function deleteDevice(deviceId) {
    if (!confirm(getTrans("confirmDelete", "Вы уверены, что хотите удалить это устройство?"))) return;
    api("/api/device/delete/", { id: deviceId }).then(() => {
      state.devices = state.devices.filter((d) => d.id !== deviceId);
      state.connections = state.connections.filter(
        (c) => c.source_device !== deviceId && c.target_device !== deviceId
      );
      if (state.modalDevice && state.modalDevice.id === deviceId) {
        hideModal(modal);
      }
      render();
    }).catch(showError);
  }

  function deleteConnection(connectionId) {
    if (!confirm(getTrans("confirmDeleteConnection", "Вы уверены, что хотите удалить это соединение?"))) return;
    api("/api/connection/delete/", { id: connectionId }).then(() => {
      state.connections = state.connections.filter((c) => c.id !== connectionId);
      render();
    }).catch(showError);
  }

  function terminalCommand(command) {
    const device = state.modalDevice;
    const clean = command.trim();
    let output = "";
    terminalOutput.textContent += `${clean}\n`;

    if (!clean) return;
    if (clean === "enable") {
      state.terminalMode = "privileged";
    } else if (clean === "configure terminal") {
      state.terminalMode = "config";
      output = "Enter configuration commands, one per line. End with CNTL/Z.";
    } else if (clean === "show ip interface brief") {
      output = Object.entries(device.interfaces || {}).map(([name, data]) => {
        return `${name.padEnd(24)}${(data.ip_address || device.ip_address || "unassigned").padEnd(18)}${data.status || "down"}`;
      }).join("\n") || "No interfaces";
    } else if (clean === "show running-config") {
      output = [
        `hostname ${device.hostname || device.name}`,
        ...Object.entries(device.interfaces || {}).map(([name, data]) => {
          return [
            `interface ${name}`,
            data.ip_address ? ` ip address ${data.ip_address} ${data.subnet_mask || device.subnet_mask || ""}` : " no ip address",
            data.status === "down" ? " shutdown" : " no shutdown",
          ].join("\n");
        }),
        device.gateway ? `ip default-gateway ${device.gateway}` : "",
      ].filter(Boolean).join("\n");
    } else if (clean.startsWith("interface ")) {
      state.terminalMode = "interface";
      state.terminalInterface = clean.replace("interface ", "").trim();
    } else if (clean.startsWith("ip address ")) {
      const parts = clean.split(/\s+/);
      if (parts.length >= 4) {
        device.ip_address = parts[2];
        device.subnet_mask = parts[3];
        document.getElementById("deviceIp").value = device.ip_address;
        document.getElementById("deviceMask").value = device.subnet_mask;
        // Also update the selected interface if we're in interface mode
        if (state.terminalInterface && device.interfaces && device.interfaces[state.terminalInterface]) {
          device.interfaces[state.terminalInterface].ip_address = parts[2];
          device.interfaces[state.terminalInterface].subnet_mask = parts[3];
        }
        output = "IP address configured";
      } else {
        output = "% Invalid command";
      }
    } else if (clean === "no shutdown") {
      if (state.terminalInterface && device.interfaces && device.interfaces[state.terminalInterface]) {
        device.interfaces[state.terminalInterface].status = "up";
      }
      device.status = "active";
      document.getElementById("deviceStatus").value = "active";
      renderInterfaces(device);
      output = `${state.terminalInterface || "Interface"} changed state to up`;
    } else if (clean === "shutdown") {
      if (state.terminalInterface && device.interfaces && device.interfaces[state.terminalInterface]) {
        device.interfaces[state.terminalInterface].status = "down";
      }
      device.status = "down";
      document.getElementById("deviceStatus").value = "down";
      renderInterfaces(device);
      output = `${state.terminalInterface || "Interface"} changed state to down`;
    } else if (clean.startsWith("ping ")) {
      const targetIp = clean.split(/\s+/)[1];
      const target = state.devices.find((candidate) => candidate.ip_address === targetIp);
      if (!target) {
        output = `Pinging ${targetIp} with 32 bytes of data:\nRequest timed out.`;
      } else {
        sourceSelect.value = device.id;
        targetSelect.value = target.id;
        startSimulation(true);
        output = `Pinging ${targetIp} with 32 bytes of data:\nSimulation started from ${device.name} to ${target.name}.`;
      }
    } else if (clean === "exit") {
      state.terminalMode = state.terminalMode === "interface" ? "config" : "exec";
      state.terminalInterface = null;
    } else {
      output = "% Invalid command";
    }

    if (output) terminalOutput.textContent += `${output}\n`;
    updatePrompt();
    terminalOutput.textContent += terminalPrompt.textContent + " ";
    terminalOutput.scrollTop = terminalOutput.scrollHeight;
  }

  function updatePrompt() {
    const host = (state.modalDevice && (state.modalDevice.hostname || state.modalDevice.name)) || "Device";
    const prompt = state.terminalMode === "privileged"
      ? `${host}#`
      : state.terminalMode === "config"
        ? `${host}(config)#`
        : state.terminalMode === "interface"
          ? `${host}(config-if)#`
          : `${host}>`;
    terminalPrompt.textContent = prompt;
  }

  function renderSimulationHistory() {
    const historyContainer = document.getElementById("simulationHistory");
    if (!historyContainer) return;
    
    historyContainer.innerHTML = state.simulationHistory.length 
      ? state.simulationHistory.map((item, index) => `
          <div class="list-row">
            <b>${new Date(item.timestamp).toLocaleString()}</b>
            <span>${item.source} → ${item.target} (${item.protocol}): ${item.success ? "✅ Успешно" : "❌ Ошибка"}</span>
          </div>
        `).join("")
      : `<p class="muted">История пуста</p>`;
  }
  
  function startSimulation(fromTerminal) {
    if (!sourceSelect.value || !targetSelect.value) {
      showError(new Error(getTrans("addMinTwoDevices", "Добавьте минимум два устройства")));
      return;
    }
    resetLinkStates();
    logEvent(getTrans("simulation", "Симуляция"), getTrans("packetLaunched", "Пакет запущен"), "warn");
    api("/api/simulation/start/", {
      source_device: sourceSelect.value,
      target_device: targetSelect.value,
      protocol: protocolSelect.value,
    }).then((data) => {
      const sourceDevice = byId(sourceSelect.value);
      const targetDevice = byId(targetSelect.value);
      
      state.simulationHistory.unshift({
        timestamp: Date.now(),
        source: sourceDevice ? sourceDevice.name : sourceSelect.value,
        target: targetDevice ? targetDevice.name : targetSelect.value,
        protocol: protocolSelect.value.toUpperCase(),
        success: data.result.success,
      });
      
      animatePath(data.result.path, data.result.success);
      renderChecks(data.result.checks);
      data.result.hops.forEach((hop, index) => logEvent(`${index + 1}. ${hop.name}`, hop.state, hop.state));
      if (fromTerminal) terminalOutput.textContent += `${data.result.message}\n`;
      
      renderSimulationHistory();
    }).catch(showError);
  }

  function animatePath(path, success) {
    if (!path || !path.length) {
      packet.style.opacity = 0;
      return;
    }
    const points = path.map(byId).filter(Boolean);
    let index = 0;
    packet.style.background = success ? "var(--netlab-ok)" : "var(--netlab-bad)";
    packet.style.left = `${points[0].x}px`;
    packet.style.top = `${points[0].y}px`;
    packet.style.opacity = 1;

    function step() {
      if (index >= points.length - 1) {
        packet.style.opacity = 0;
        return;
      }
      const current = points[index];
      const next = points[index + 1];
      const line = linksLayer.querySelector(`[data-key="${linkKey(current.id, next.id)}"]`);
      if (line) line.classList.add(success ? "is-success" : "is-error");
      index += 1;
      packet.style.left = `${next.x}px`;
      packet.style.top = `${next.y}px`;
      setTimeout(step, 650);
    }
    setTimeout(step, 220);
  }

  function checkNetwork() {
    api("/api/network/check/", {
      source_device: sourceSelect.value || null,
      target_device: targetSelect.value || null,
    }).then(renderChecks).catch(showError);
  }

  function renderChecks(result) {
    checkList.innerHTML = "";
    (result.ok || []).forEach((message) => {
      checkList.insertAdjacentHTML("beforeend", `<div class="check-row ok">✓ ${escapeHtml(message)}</div>`);
    });
    (result.issues || []).forEach((issue) => {
      checkList.insertAdjacentHTML("beforeend", `<div class="check-row bad">✗ ${escapeHtml(issue.message)}</div>`);
    });
    if (!checkList.innerHTML) {
      checkList.innerHTML = `<p class="muted">${getTrans("noCheckData", "Нет данных проверки.")}</p>`;
    }
  }

  function resetLinkStates() {
    linksLayer.querySelectorAll(".link").forEach((line) => {
      line.classList.remove("is-active", "is-success", "is-error");
    });
  }

  function logEvent(title, text, stateName) {
    eventLog.insertAdjacentHTML("afterbegin", `
      <div class="event-row ${stateName || ""}">
        <b>${escapeHtml(title)}</b>
        <span>${escapeHtml(text)}</span>
      </div>
    `);
  }

  function labelCable(cable) {
    return { auto: "Auto", straight: "Straight Through", crossover: "Cross Over", fiber: "Fiber" }[cable] || cable;
  }

  function showError(error) {
    logEvent(getTrans("error", "Ошибка"), error.message || String(error), "error");
  }

  function showModal(element) {
    element.classList.add("is-open");
    element.setAttribute("aria-hidden", "false");
  }

  function hideModal(element) {
    if (element === modal && hasChanges()) {
      if (!confirm(getTrans("unsavedChanges", "У вас есть несохраненные изменения. Вы уверены, что хотите закрыть?"))) {
        return;
      }
    }
    element.classList.remove("is-open");
    element.setAttribute("aria-hidden", "true");
    state.modalDevice = null;
    state.originalDeviceData = null;
  }

  function escapeHtml(value) {
    return String(value).replace(/[&<>"']/g, (char) => ({
      "&": "&amp;",
      "<": "&lt;",
      ">": "&gt;",
      '"': "&quot;",
      "'": "&#039;",
    }[char]));
  }

  document.querySelectorAll(".palette-item").forEach((button) => {
    button.addEventListener("click", () => {
      const rect = canvas.getBoundingClientRect();
      api("/api/device/add/", {
        type: button.dataset.deviceType,
        x: Math.round(rect.width / 2 + Math.random() * 120 - 60),
        y: Math.round(rect.height / 2 + Math.random() * 120 - 60),
      }).then((data) => {
        state.devices.push(data.device);
        render();
      }).catch(showError);
    });
  });

  document.querySelectorAll(".cable-item").forEach((button) => {
    button.addEventListener("click", () => {
      document.querySelectorAll(".cable-item").forEach((item) => item.classList.remove("is-active"));
      button.classList.add("is-active");
      state.selectedCable = button.dataset.cable;
      state.pendingSource = null;
      modePill.textContent = `${getTrans("cableLabel", "Кабель")}: ${labelCable(state.selectedCable)}`;
      highlightNode(null);
    });
  });

  document.getElementById("saveDevice").addEventListener("click", saveModalDevice);
  document.getElementById("closeModal").addEventListener("click", () => hideModal(modal));
  document.getElementById("helpBtn").addEventListener("click", () => showModal(helpModal));
  document.getElementById("closeHelp").addEventListener("click", () => hideModal(helpModal));
  document.getElementById("runBtn").addEventListener("click", () => startSimulation(false));
  document.getElementById("checkBtn").addEventListener("click", checkNetwork);
  


  document.getElementById("autoIpBtn").addEventListener("click", () => {
    let ipCounter = 10;
    const updates = [];
    state.devices.forEach((device) => {
      if (device.type !== "switch" && device.type !== "hub") {
        device.ip_address = `192.168.1.${ipCounter}`;
        device.subnet_mask = "255.255.255.0";
        ipCounter += 1;
        updates.push(api("/api/device/update/", { id: device.id, ip_address: device.ip_address, subnet_mask: device.subnet_mask }));
      }
    });
    Promise.all(updates).then(() => {
      render();
      logEvent(getTrans("autoIp", "Авто IP"), getTrans("autoIpSet", "IP-адреса автоматически назначены"), "ok");
    }).catch(showError);
  });

  const toggleSidebarBtn = document.getElementById("toggleSidebarBtn");
  if (toggleSidebarBtn) {
    toggleSidebarBtn.addEventListener("click", () => {
      const sidebar = document.querySelector("aside.fixed");
      const netlab = document.querySelector(".netlab");
      if (sidebar && netlab) {
        sidebar.classList.toggle("hidden");
        sidebar.classList.toggle("flex");
        sidebar.classList.toggle("lg:flex");
        netlab.classList.toggle("lg:ml-64");
      }
    });
  }

  document.querySelectorAll(".tab").forEach((tab) => {
    tab.addEventListener("click", () => {
      document.querySelectorAll(".tab").forEach((item) => item.classList.remove("is-active"));
      document.querySelectorAll(".tab-panel").forEach((panel) => panel.classList.remove("is-active"));
      tab.classList.add("is-active");
      document.getElementById(`tab-${tab.dataset.tab}`).classList.add("is-active");
    });
  });

  // Terminal autocomplete commands
  const terminalCommands = ["enable", "configure terminal", "show ip interface brief", "show running-config", "interface", "ip address", "no shutdown", "shutdown", "ping", "exit"];
  
  document.getElementById("terminalForm").addEventListener("submit", (event) => {
    event.preventDefault();
    terminalCommand(terminalInput.value);
    terminalInput.value = "";
  });
  
  terminalInput.addEventListener("keydown", (event) => {
    if (event.key === "Tab") {
      event.preventDefault();
      const input = terminalInput.value.trim();
      if (!input) return;
      
      // Find matching commands
      const matches = terminalCommands.filter(cmd => cmd.toLowerCase().startsWith(input.toLowerCase()));
      if (matches.length === 1) {
        terminalInput.value = matches[0];
      } else if (matches.length > 1) {
        terminalOutput.textContent += `\n${matches.join("  ")}\n`;
        terminalOutput.scrollTop = terminalOutput.scrollHeight;
      }
    }
  });

  // Add delete button to modal
  const modalFooter = document.querySelector(".modal__footer");
  if (modalFooter) {
    const deleteBtn = document.createElement("button");
    deleteBtn.className = "netlab-btn";
    deleteBtn.style.background = "var(--netlab-bad)";
    deleteBtn.style.color = "white";
    deleteBtn.textContent = getTrans("delete", "Удалить");
    deleteBtn.addEventListener("click", () => {
      if (state.modalDevice) {
        deleteDevice(state.modalDevice.id);
      }
    });
    modalFooter.insertBefore(deleteBtn, modalFooter.firstChild);
  }

  api("/api/topology/").then((topology) => {
    state.topology = topology;
    state.devices = topology.devices || [];
    state.connections = topology.connections || [];
    render();
    if (!localStorage.getItem("netlab-help-seen")) {
      showModal(helpModal);
      localStorage.setItem("netlab-help-seen", "1");
    }
  }).catch(showError);
})();
