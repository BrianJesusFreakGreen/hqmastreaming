// Overlay renderer for live listener state.
// Kept intentionally small/easy to tweak while data format is still being learned.

function text(value, fallback = "") {
  return value === undefined || value === null || value === "" ? fallback : String(value);
}

function renderTable(containerId, rows) {
  const container = document.getElementById(containerId);
  if (!container) return;

  container.innerHTML = "";

  (rows || []).forEach((row) => {
    const isLeader = Number(row.pos) === 1;
    const keys = isLeader ? ["pos", "car", "name", "last"] : ["pos", "car", "name", "gap"];

    keys.forEach((key) => {
      const cell = document.createElement("div");
      cell.className = `cell ${key}`;
      cell.textContent = text(row[key], "-");
      container.appendChild(cell);
    });
  });
}

function renderHeader(data) {
  // event_name/session_name/track_status/laps_remaining are provided by listener.py
  // and backed by the new stream packet handlers.
  document.getElementById("event_name").textContent = text(data.event_name, "Waiting for race...");
  document.getElementById("session_name").textContent = text(data.session_name, "");
  document.getElementById("track_status").textContent = text(data.track_status, "-");

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
