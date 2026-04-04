function renderTable(containerId, rows) {
  const el = document.getElementById(containerId);
  el.innerHTML = "";

  /* const headers = ["Pos", "Car", "Name", "Last", "Gap"];
  headers.forEach(h => {
    const c = document.createElement("div");
    c.className = "cell";
    c.textContent = h;
    el.appendChild(c);
  });
*/
  rows.forEach(row => {
    if (row.pos === 1){
        ["pos", "car", "name", "last"].forEach(key => {
        const c = document.createElement("div");
        c.className = "cell " + key;
        c.textContent = row[key];
        el.appendChild(c);
        });
    }
    else{
        ["pos", "car", "name", "gap"].forEach(key => {
        const c = document.createElement("div");
        c.className = "cell " + key;
        c.textContent = row[key];
        el.appendChild(c);
        });
    }
  });
}

async function refreshOverlay() {
  const res = await fetch("/api/state");
  const data = await res.json();

  document.getElementById("event_name").textContent = data.event_name;
  document.getElementById("session_name").textContent = data.session_name;
  document.getElementById("track_status").textContent = data.track_status;
  document.getElementById("laps_remaining").textContent = data.laps_remaining;

  renderTable("leaders_grid", data.leaders);
  renderTable("rest_grid", data.rest);
}

refreshOverlay();
setInterval(refreshOverlay, 1000);