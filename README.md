# Cron Dashboard

A lightweight GitHub Pages dashboard powered by GitHub Actions cron jobs.
No servers, no databases — just Python scripts + static JSON + one HTML file.

## Live Jobs

| Job | Schedule | Script | Output |
|-----|----------|--------|--------|
| Chess Tournaments | Every Monday 09:00 IST | `scripts/fetch_chess.py` | `data/chess.json` |
| Weather Forecast  | Every day 07:30 IST    | `scripts/fetch_weather.py` | `data/weather.json` |

## Setup

### 1. Fork / clone this repo

```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPO
```

### 2. Enable GitHub Pages

Go to **Settings → Pages → Source** and set it to **Deploy from branch: `main`, folder `/` (root)**.

Your dashboard will be live at `https://YOUR_USERNAME.github.io/YOUR_REPO/`.

### 3. Run workflows for the first time

Go to **Actions → Chess Tournament Tracker → Run workflow** (and same for Weather Forecast).
This populates `data/chess.json` and `data/weather.json` immediately.

After that, GitHub Actions runs them automatically on schedule.

### 4. Customise cities (weather)

Edit `scripts/fetch_weather.py` and update the `CITIES` list:

```python
CITIES = [
    {"name": "Pune",      "lat": 21.1904, "lon": 81.2849},
    {"name": "Mumbai",    "lat": 22.0796, "lon": 82.1391},
    {"name": "Bengaluru", "lat": 21.2514, "lon": 81.6296},
]
```

## Project Structure

```
.github/
  workflows/
    chess.yml          # weekly cron, commits data/chess.json
    weather.yml        # daily cron, commits data/weather.json
scripts/
  fetch_chess.py       # scrapes chessevents.co.in (stdlib only)
  fetch_weather.py     # fetches Open-Meteo API (stdlib only)
data/
  chess.json           # auto-updated by GitHub Actions
  weather.json         # auto-updated by GitHub Actions
index.html             # GitHub Pages frontend (vanilla JS)
```

## Dependencies

**Zero** — everything uses Python stdlib (`urllib`, `html.parser`, `json`, `pathlib`).
The weather API ([Open-Meteo](https://open-meteo.com)) is free with no API key.

## Adding New Jobs

1. Create `scripts/fetch_something.py` that writes to `data/something.json`
2. Add `.github/workflows/something.yml` with your cron schedule
3. Add a new tab in `index.html` that fetches `./data/something.json`

See the **💡 Ideas** tab in the dashboard for inspiration.
