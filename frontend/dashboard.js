// UrbanResQ Dashboard JS (Charts + Map + Table)
// Requires: Chart.js + Leaflet

let waterChart, tempChart, riskDonut;
let map, markersLayer;

const els = {
  backendUrl: document.getElementById("backendUrl"),
  locationId: document.getElementById("locationId"),
  btnRefresh: document.getElementById("btnRefresh"),
  statusText: document.getElementById("statusText"),
  statusPill: document.getElementById("statusPill"),

  readingTime: document.getElementById("readingTime"),
  waterText: document.getElementById("waterText"),
  readingSub: document.getElementById("readingSub"),

  riskTime: document.getElementById("riskTime"),
  riskText: document.getElementById("riskText"),
  riskReasons: document.getElementById("riskReasons"),

  alertsMeta: document.getElementById("alertsMeta"),
  alertsList: document.getElementById("alertsList"),

  readingsTable: document.getElementById("readingsTable"),

  riskScoreText: document.getElementById("riskScoreText"),
};

function apiBase() {
  return els.backendUrl.value.replace(/\/$/, "");
}

function setStatus(ok, msg) {
  els.statusText.textContent = msg;

  els.statusText.classList.remove("ok", "bad");
  els.statusPill.classList.remove("ok", "bad");

  if (ok === true) {
    els.statusText.classList.add("ok");
    els.statusPill.classList.add("ok");
    els.statusPill.textContent = "Live ✓";
  } else if (ok === false) {
    els.statusText.classList.add("bad");
    els.statusPill.classList.add("bad");
    els.statusPill.textContent = "Offline";
  } else {
    els.statusPill.textContent = "Connecting…";
  }
}

function fmtTime(iso) {
  if (!iso) return "—";
  try {
    const d = new Date(iso);
    return d.toLocaleString();
  } catch {
    return iso;
  }
}

function riskScoreFrom(reading) {
  // Simple score: water dominates + temp influences
  // tweak anytime you want
  const water = Number(reading?.water_level_cm ?? 0);
  const temp = Number(reading?.temp_c ?? 0);

  const waterScore = Math.min(100, Math.max(0, (water / 100) * 100)); // 0-100 cm -> 0-100
  const tempScore = Math.min(100, Math.max(0, ((temp - 25) / 15) * 100)); // 25-40C -> 0-100

  const score = Math.round(waterScore * 0.7 + tempScore * 0.3);
  return Math.min(100, Math.max(0, score));
}

function scoreLabel(score) {
  if (score >= 70) return { label: "HIGH", css: "danger" };
  if (score >= 40) return { label: "MEDIUM", css: "warn" };
  return { label: "LOW", css: "good" };
}

async function fetchJson(url) {
  const res = await fetch(url);
  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new Error(`${res.status} ${res.statusText} ${text}`);
  }
  return await res.json();
}

function buildTable(rows) {
  const head = `
    <tr>
      <th>Time</th>
      <th>Water (cm)</th>
      <th>Temp (°C)</th>
      <th>Rain (mm)</th>
      <th>Humidity</th>
      <th>Salinity</th>
      <th>Device</th>
    </tr>
  `;

  const body = (rows || []).map(r => `
    <tr>
      <td class="muted">${fmtTime(r.timestamp)}</td>
      <td>${r.water_level_cm ?? "—"}</td>
      <td>${r.temp_c ?? "—"}</td>
      <td>${r.rainfall_mm ?? "—"}</td>
      <td>${r.humidity ?? "—"}</td>
      <td>${r.salinity ?? "—"}</td>
      <td class="muted">${r.device_id ?? "—"}</td>
    </tr>
  `).join("");

  els.readingsTable.innerHTML = head + body;
}

function renderAlerts(alerts) {
  if (!alerts || alerts.length === 0) {
    els.alertsList.innerHTML = `<div class="muted">No alerts.</div>`;
    els.alertsMeta.textContent = "0 alert(s)";
    return;
  }

  els.alertsMeta.textContent = `${alerts.length} alert(s)`;

  els.alertsList.innerHTML = alerts.map(a => {
    const sev = (a.severity || "INFO").toUpperCase();
    const type = (a.type || "ALERT").toUpperCase();
    const time = fmtTime(a.timestamp);

    let badgeClass = "badge";
    if (sev === "HIGH" || sev === "DANGER") badgeClass += " badge-danger";
    else if (sev === "MEDIUM" || sev === "WARN") badgeClass += " badge-warn";
    else badgeClass += " badge-good";

    return `
      <div class="alert-item">
        <div class="alert-top">
          <span class="${badgeClass}">${sev}</span>
          <span class="muted">${type}</span>
          <span class="muted" style="margin-left:auto">${time}</span>
        </div>
        <div class="alert-msg">${a.message || "—"}</div>
        <div class="muted tiny">location: ${a.location_id || "—"}</div>
      </div>
    `;
  }).join("");
}

function initCharts() {
  const waterCtx = document.getElementById("waterChart");
  const tempCtx = document.getElementById("tempChart");
  const donutCtx = document.getElementById("riskDonut");

  waterChart = new Chart(waterCtx, {
    type: "line",
    data: { labels: [], datasets: [{ label: "Water level (cm)", data: [], tension: 0.35 }] },
    options: {
      responsive: true,
      plugins: { legend: { labels: { color: "#eaf0ff" } } },
      scales: {
        x: { ticks: { color: "rgba(234,240,255,.7)" }, grid: { color: "rgba(234,240,255,.08)" } },
        y: { ticks: { color: "rgba(234,240,255,.7)" }, grid: { color: "rgba(234,240,255,.08)" } }
      }
    }
  });

  tempChart = new Chart(tempCtx, {
    type: "line",
    data: { labels: [], datasets: [{ label: "Temperature (°C)", data: [], tension: 0.35 }] },
    options: {
      responsive: true,
      plugins: { legend: { labels: { color: "#eaf0ff" } } },
      scales: {
        x: { ticks: { color: "rgba(234,240,255,.7)" }, grid: { color: "rgba(234,240,255,.08)" } },
        y: { ticks: { color: "rgba(234,240,255,.7)" }, grid: { color: "rgba(234,240,255,.08)" } }
      }
    }
  });

  riskDonut = new Chart(donutCtx, {
    type: "doughnut",
    data: {
      labels: ["Risk", "Remaining"],
      datasets: [{ data: [0, 100], borderWidth: 0 }]
    },
    options: {
      cutout: "72%",
      plugins: { legend: { display: false } }
    }
  });
}

function initMap() {
  map = L.map("map", { zoomControl: true }).setView([1.3521, 103.8198], 11);

  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 19,
    attribution: "© OpenStreetMap"
  }).addTo(map);

  markersLayer = L.layerGroup().addTo(map);
}

function markerIcon(color) {
  // simple circle marker style using DivIcon
  const html = `<div style="
    width:14px;height:14px;border-radius:999px;
    background:${color};
    box-shadow:0 0 0 3px rgba(255,255,255,.18), 0 10px 18px rgba(0,0,0,.35);
  "></div>`;

  return L.divIcon({ html, className: "", iconSize: [14, 14], iconAnchor: [7, 7] });
}

function scoreColor(score) {
  if (score >= 70) return "#fb7185";
  if (score >= 40) return "#fbbf24";
  return "#4ade80";
}

async function refreshAll() {
  const base = apiBase();
  const loc = els.locationId.value.trim();

  try {
    setStatus(null, "Fetching…");

    const [latest, risk, alerts, history, locations] = await Promise.all([
      fetchJson(`${base}/api/readings/latest?location_id=${encodeURIComponent(loc)}`),
      fetchJson(`${base}/api/risk/latest?location_id=${encodeURIComponent(loc)}`),
      fetchJson(`${base}/api/alerts?status=open`),
      fetchJson(`${base}/api/readings/history?location_id=${encodeURIComponent(loc)}&limit=40`),
      fetchJson(`${base}/api/locations`)
    ]);

    // Latest reading card
    els.readingTime.textContent = fmtTime(latest.timestamp);
    els.waterText.textContent = `Water: ${latest.water_level_cm ?? "—"} cm`;
    els.readingSub.textContent =
      `Temp: ${latest.temp_c ?? "—"} °C | Salinity: ${latest.salinity ?? "—"} | Humidity: ${latest.humidity ?? "—"}% | Rain: ${latest.rainfall_mm ?? "—"} mm`;

    // Risk card
    els.riskTime.textContent = fmtTime(risk.timestamp);
    els.riskText.textContent = (risk.level || "—").toUpperCase();
    els.riskReasons.textContent = `Reasons: ${(risk.reasons || []).join(", ") || "—"}`;

    // Alerts
    renderAlerts(alerts);

    // Table
    buildTable(history);

    // Charts (history)
    const labels = (history || []).slice().reverse().map(r => {
      try {
        const d = new Date(r.timestamp);
        return d.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
      } catch {
        return r.timestamp;
      }
    });

    const waterData = (history || []).slice().reverse().map(r => r.water_level_cm ?? 0);
    const tempData = (history || []).slice().reverse().map(r => r.temp_c ?? 0);

    waterChart.data.labels = labels;
    waterChart.data.datasets[0].data = waterData;
    waterChart.update();

    tempChart.data.labels = labels;
    tempChart.data.datasets[0].data = tempData;
    tempChart.update();

    // Donut from latest reading
    const score = riskScoreFrom(latest);
    els.riskScoreText.textContent = score;

    riskDonut.data.datasets[0].data = [score, 100 - score];
    // Let Chart.js auto-colors? We'll set dynamically here:
    riskDonut.data.datasets[0].backgroundColor = [scoreColor(score), "rgba(234,240,255,.12)"];
    riskDonut.update();

    // Map markers
    markersLayer.clearLayers();
    const latestScore = score;

    (locations || []).forEach(locItem => {
      const isSelected = locItem.id === loc;
      const color = isSelected ? scoreColor(latestScore) : "rgba(102,227,255,.75)";
      const marker = L.marker([locItem.lat, locItem.lon], { icon: markerIcon(color) });

      marker.bindPopup(`
        <b>${locItem.name}</b> (${locItem.id})<br/>
        region: ${locItem.region}<br/>
        ${isSelected ? `<b>Current score:</b> ${latestScore}/100` : ""}
      `);

      marker.addTo(markersLayer);
    });

    setStatus(true, "Live ✓ Fetched successfully");
  } catch (err) {
    console.error(err);
    setStatus(false, `Failed: ${err.message || err}`);
  }
}

function boot() {
  initCharts();
  initMap();

  els.btnRefresh.addEventListener("click", refreshAll);

  // first load
  refreshAll();

  // auto refresh
  setInterval(refreshAll, 3000);
}

boot();
