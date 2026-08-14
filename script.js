// ────────────────────────────────────────────────
//  TABS
// ────────────────────────────────────────────────
document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
        document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
        btn.classList.add('active');
        document.getElementById('tab-' + btn.dataset.tab).classList.add('active');
    });
});

// ────────────────────────────────────────────────
//  HELPERS
// ────────────────────────────────────────────────

function dayName(isoDate, index) {
    if (index === 0) return 'Today';
    if (index === 1) return 'Tomorrow';
    try {
        return new Date(isoDate + 'T12:00:00').toLocaleDateString('en-IN', {
            weekday: 'short',
            day: 'numeric',
            month: 'short'
        });
    } catch {
        return isoDate;
    }
}

async function loadJSON(path) {
    const r = await fetch(path);
    if (!r.ok) throw new Error(`HTTP ${r.status}`);
    return r.json();
}

// ────────────────────────────────────────────────
//  CHESS
// ────────────────────────────────────────────────
let allTournaments = [];

function renderChess(tournaments) {
    const monthSel = document.getElementById('filterMonth');
    const locSel = document.getElementById('filterLocation');
    const search = document.getElementById('filterSearch').value.trim().toLowerCase();
    const selMonth = monthSel.value;
    const selLoc = locSel.value;

    let list = tournaments;
    if (selMonth) list = list.filter(t => t.month === selMonth);
    if (selLoc) list = list.filter(t => t.location === selLoc);
    if (search) list = list.filter(t =>
        (t.name || '').toLowerCase().includes(search) ||
        (t.category || '').toLowerCase().includes(search));

    // Group by month
    const groups = {};
    list.forEach(t => {
        const m = t.month || '2026';
        if (!groups[m]) groups[m] = [];
        groups[m].push(t);
    });

    const content = document.getElementById('chessContent');

    if (list.length === 0) {
        content.innerHTML = `<div class="empty-state">
      <div class="big">♟</div>
      No tournaments match the current filters.<br>Try clearing filters or wait for the weekly update.
    </div>`;
        return;
    }

    let html = '';
    Object.entries(groups).forEach(([month, items]) => {
        html += `<div class="month-group">
      <div class="month-label">◆ ${month} — ${items.length} event${items.length !== 1 ? 's' : ''}</div>
      <table class="t-table">
        <thead><tr>
          <th>Tournament</th>
          <th>Date</th>
          <th>Location</th>
          <th>Venue</th>
        </tr></thead>
        <tbody>`;
        items.forEach(t => {
            html += `<tr>
        <td class="t-name">${esc(t.name)}
        <span>${t.category ? `<span class="t-category">${esc(t.category)}</span>` : ""}</span>
        </td>
        <td class="t-date">${esc(t.date)}</td>
        <td class="t-location">${esc(t.location) || '<span style="color:var(--muted)">—</span>'}</td>
        <td class="t-venue">${esc(t.venue)}</td>

      </tr>`;
        });
        html += `</tbody></table></div>`;
    });

    content.innerHTML = html;
}

function esc(s) {
    if (!s) return '';
    return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

async function initChess() {
    try {
        const data = await loadJSON('./data/chess.json');
        document.getElementById('chessUpdated').textContent = data.updated;
        allTournaments = data.tournaments || [];

        if (allTournaments.length === 0) {
            document.getElementById('chessContent').innerHTML = `<div class="empty-state">
        <div class="big">♟</div>
        No data yet. The workflow runs every Monday and will populate this on first run.<br><br>
        You can also trigger it manually from the Actions tab in your GitHub repository.
      </div>`;
            return;
        }

        // Stats bar
        const months = [...new Set(allTournaments.map(t => t.month).filter(Boolean))];
        const locs = [...new Set(allTournaments.map(t => t.location).filter(Boolean))];
        document.getElementById('chessStats').style.display = 'flex';
        document.getElementById('chessStats').innerHTML = `
      <div class="stat"><div class="stat-val">${allTournaments.length}</div><div class="stat-lbl">Tournaments</div></div>
      <div class="stat"><div class="stat-val">${months.length}</div><div class="stat-lbl">Months</div></div>
      <div class="stat"><div class="stat-val">${locs.length}</div><div class="stat-lbl">Locations</div></div>
    `;

        // Populate filters
        const monthSel = document.getElementById('filterMonth');
        const locSel = document.getElementById('filterLocation');
        months.forEach(m => monthSel.append(Object.assign(document.createElement('option'), {
            value: m,
            textContent: m
        })));
        locs.sort().forEach(l => locSel.append(Object.assign(document.createElement('option'), {
            value: l,
            textContent: l
        })));
        document.getElementById('chessFilters').style.display = 'flex';

        renderChess(allTournaments);

        ['filterMonth', 'filterLocation', 'filterSearch'].forEach(id => {
            document.getElementById(id).addEventListener('input', () => renderChess(allTournaments));
            document.getElementById(id).addEventListener('change', () => renderChess(allTournaments));
        });
        document.getElementById('clearFilters').addEventListener('click', () => {
            document.getElementById('filterMonth').value = '';
            document.getElementById('filterLocation').value = '';
            document.getElementById('filterSearch').value = '';
            renderChess(allTournaments);
        });

    } catch (e) {
        document.getElementById('chessContent').innerHTML = `<div class="empty-state">
      <div class="big">⚠</div>
      Could not load chess data.<br><small style="font-family:var(--font-mono)">${esc(e.message)}</small>
    </div>`;
    }
}

// ────────────────────────────────────────────────
//  WEATHER
// ────────────────────────────────────────────────
function tempColor(t) {
    if (t >= 40) return '#e05040';
    if (t >= 35) return '#f08030';
    if (t >= 28) return '#f0a020';
    if (t >= 20) return '#a0c050';
    return '#5090d8';
}

async function initWeather() {
    try {
        const data = await loadJSON('./data/weather.json');
        document.getElementById('weatherUpdated').textContent = data.updated;
        const cities = data.cities || [];

        if (cities.length === 0) {
            document.getElementById('weatherContent').innerHTML = `<div class="empty-state">
        <div class="big">🌦</div>
        No weather data yet. The workflow runs daily and will populate this on first run.<br><br>
        Trigger it manually from the Actions tab.
      </div>`;
            return;
        }

        let html = '<div class="city-grid">';
        cities.forEach(city => {
            const today = city.forecast[0];
            const rest = city.forecast.slice(1);
            html += `<div class="city-card">
        <div class="city-head">
          <div>
            <div class="city-name">${esc(city.name)}</div>
            <div class="city-today-condition">${today.emoji} ${esc(today.condition)}</div>
            <div class="city-meta">
              <span>💧 ${today.precipitation_mm ?? 0} mm</span>
              <span>🌬 ${today.wind_kmh ?? '—'} km/h</span>
              <span>☀ UV ${today.uv_index ?? '—'}</span>
              ${today.sunrise ? `<span>↑ ${today.sunrise}</span>` : ''}
              ${today.sunset ? `<span>↓ ${today.sunset}</span>` : ''}
            </div>
          </div>
          <div style="text-align:right">
            <div class="city-today-temp" style="color:${tempColor(today.max_temp)}">${today.max_temp ?? '—'}°</div>
            <div class="city-today-sub">
              Hi <span style="color:${tempColor(today.max_temp)}">${today.max_temp}°</span>
              &nbsp; Lo <span style="color:var(--muted)">${today.min_temp}°C</span>
            </div>
            ${today.feels_like_max != null ? `<div class="city-today-sub">Feels ${today.feels_like_max}°C</div>` : ''}
          </div>
        </div>
        <div class="forecast-list">`;

            rest.forEach((d, i) => {
                const pct = Math.min(100, (d.precip_probability ?? 0));
                html += `<div class="forecast-row">
          <div class="f-day">${dayName(d.date, i + 1)}</div>
          <div class="f-emoji">${d.emoji}</div>
          <div>
            <div class="f-cond">${esc(d.condition)}</div>
            ${pct > 0 ? `<div class="precip-bar-wrap"><div class="precip-bar-fill" style="width:${pct}%"></div></div>` : ''}
          </div>
          <div class="f-temps">
            <span class="f-hi">${d.max_temp}°</span>
            <span class="f-lo"> / ${d.min_temp}°</span>
          </div>
        </div>`;
            });

            html += `</div></div>`;
        });
        html += '</div>';
        document.getElementById('weatherContent').innerHTML = html;
    } catch (e) {
        document.getElementById('weatherContent').innerHTML = `<div class="empty-state">
      <div class="big">⚠</div>
      Could not load weather data.<br><small style="font-family:var(--font-mono)">${esc(e.message)}</small>
    </div>`;
    }
}

// ────────────────────────────────────────────────
//  IDEAS
// ────────────────────────────────────────────────
const IDEAS = [
    {
        icon: '🏏',
        name: 'Cricket Match Tracker',
        desc: 'Scrape upcoming local & state cricket schedules from CGCA or BCCI. Group by team, filter by venue.',
        tag: 'weekly · urllib + html.parser',
    },
    {
        icon: '⛽',
        name: 'Petrol / Diesel Prices',
        desc: 'Indian Oil publishes daily city-wise fuel prices. Track price changes over time with a simple diff chart.',
        tag: 'daily · urllib + json',
    },
    {
        icon: '🌫️',
        name: 'Air Quality Index',
        desc: 'OpenAQ API provides free AQI for Indian cities. Alert when PM2.5 or PM10 crosses danger thresholds.',
        tag: 'hourly · urllib + json',
    },
    {
        icon: '🛒',
        name: 'Mandi Market Rates',
        desc: 'AGMARKNET provides wholesale vegetable/grain prices. Track tomato, onion, potato — the household staples.',
        tag: 'daily · urllib + csv',
    },
    {
        icon: '🚆',
        name: 'Train Seat Availability',
        desc: 'Use the RailAPI or scrape IRCTC status for key routes. Notify when tickets open or waitlist drops.',
        tag: 'daily · urllib',
    },
    {
        icon: '📋',
        name: 'Exam / Result Alerts',
        desc: 'Monitor CGBSE or university result pages for content changes using a simple hash comparison between runs.',
        tag: 'daily · urllib + hashlib',
    },
    {
        icon: '💡',
        name: 'Power Outage Schedule',
        desc: 'Scrape CSPDCL load-shedding timetable and display area-wise schedule. Highlight upcoming outages.',
        tag: 'weekly · urllib + html.parser',
    },
    {
        icon: '🗞️',
        name: 'Local News Digest',
        desc: 'Fetch RSS feeds from local CG news outlets. Deduplicate, rank by freshness, and show a clean daily digest.',
        tag: 'daily · urllib + xml.etree',
    },
];
/*
document.getElementById('ideasGrid').innerHTML = IDEAS.map(idea => `
  <div class="idea-card">
    <div class="idea-icon">${idea.icon}</div>
    <div class="idea-name">${idea.name}</div>
    <div class="idea-desc">${idea.desc}</div>
    <div class="idea-tag">${idea.tag}</div>
  </div>
`).join('');
*/

// ────────────────────────────────────────────────
//  BOOT
// ────────────────────────────────────────────────
initChess();
initWeather();
