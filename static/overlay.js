// Overlay renderer for live listener state.
// Kept intentionally small/easy to tweak while data format is still being learned.

function text(value, fallback = "") {
  return value === undefined || value === null || value === "" ? fallback : String(value);
}

function formatDriverName(row) {
  const firstName = text(row.first_name).trim();
  const lastName = text(row.last_name).trim();

  if (firstName && lastName) return `${firstName[0]}. ${lastName}`;
  if (lastName) return lastName;
  if (firstName) return firstName;
  return text(row.name).trim();
}

function formatLastLap(value) {
  const raw = text(value).trim();
  if (!raw) return "";

  const match = raw.match(/^(?:\d+:)?(\d{2}):(\d{2})\.(\d{3})$/);
  if (!match) return raw;

  return `${match[2]}.${match[3]}`;
}

function renderTable(containerId, rows) {
  const container = document.getElementById(containerId);
  if (!container) return;

  container.innerHTML = "";

  (rows || []).forEach((row) => {
    const isLeader = Number(row.pos) === 1;
    const keys = isLeader ? ["pos", "car", "name", "last"] : ["pos", "car", "name", "gap"];

    keys.forEach((key) => {
      const entry = document.createElement("div");
      entry.className = `entry ${key}`;
      const keyText = document.createElement("div");
      keyText.className = 'text';
      const value =
        key === "name" ? formatDriverName(row) :
        key === "last" ? formatLastLap(row[key]) :
        row[key];
      keyText.textContent = text(value, "-");
      container.appendChild(entry);
      entry.appendChild(keyText);
    });
  });
}

function renderHeader(data) {
  // event_name/session_name/track_status/laps_remaining are provided by listener.py
  // and backed by the new stream packet handlers.
  document.getElementById("event_name").textContent = text(data.event_name, "Waiting for race...");
  document.getElementById("session_name").textContent = text(data.session_name, "");
  const statusEl = document.getElementById("track_status");
  const status = text(data.track_status, "-");
  statusEl.textContent = status;  //Set's Status In Element
  
  //change track_status class name based on flag
  //rMon does not report white
  // TODO compare leaders laps/lapsremaining with total race distance to add className of white-flag
  const normalizedStatus = status.toLowerCase();
  if(normalizedStatus.includes("green")){
    statusEl.className = "green-flag";
  }else if (normalizedStatus.includes("yellow")){
    statusEl.className = "yellow-flag";
  }else if (normalizedStatus.includes("red")){
    statusEl.className = "red-flag";
  }else if (normalizedStatus.includes("finish")){
    statusEl.className = "checkered-flag";
  }

  const lapsRemaining = data.laps_remaining;
  document.getElementById("laps_remaining").textContent =
    lapsRemaining === null || lapsRemaining === undefined ? "-" : String(lapsRemaining);
}

async function refreshOverlay() {
  try {
    const response = await fetch("/api/state", { cache: "no-store" });
    if (!response.ok) return;

    const data = await response.json();
    renderHeader(data);

    // Preserve the existing split layout in overlay.html.
    renderTable("leaders_grid", data.leaders || []);
    renderTable("rest_grid", data.rest || []);
  } catch {
    // Keep silent in production overlay loop; next poll will retry.
  }
}

refreshOverlay();
setInterval(refreshOverlay, 1000);
