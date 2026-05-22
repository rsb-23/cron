#!/usr/bin/env python3
"""
Weekly scraper for Chhattisgarh chess tournaments.
Source: https://chessevents.co.in/chhattisgarh-chess-tournament/
Output: data/chess.json
Run via: python scripts/fetch_chess.py
"""

import json
import re
import urllib.request
from datetime import datetime
from pathlib import Path

from bs4 import BeautifulSoup

URL = "https://chessevents.co.in/chhattisgarh-chess-tournament/"

MONTH_ABBR = {
    "jan": 1,
    "feb": 2,
    "mar": 3,
    "apr": 4,
    "may": 5,
    "jun": 6,
    "jul": 7,
    "aug": 8,
    "sep": 9,
    "oct": 10,
    "nov": 11,
    "dec": 12,
    "january": 1,
    "february": 2,
    "march": 3,
    "april": 4,
    "june": 6,
    "july": 7,
    "august": 8,
    "september": 9,
    "october": 10,
    "november": 11,
    "december": 12,
}


def parse_date(raw: str) -> str:
    """
    Parse various date formats into ISO YYYY-MM-DD.
    Falls back to year-only or empty string.
    """
    raw = raw.strip()
    # Try common formats directly
    for fmt in (
        "%d %b %Y",
        "%d %B %Y",
        "%b %d, %Y",
        "%B %d, %Y",
        "%Y-%m-%d",
        "%d/%m/%Y",
        "%d-%m-%Y",
        "%d.%m.%Y",
        "%d %b %y",
        "%d %B %y",
    ):
        try:
            return datetime.strptime(raw, fmt).strftime("%Y-%m-%d")
        except ValueError:
            pass

    # Handle date ranges like "15-17 Jan 2025" or "Jan 15-17, 2025"
    range_match = re.match(r"(\d{1,2})[\s\-–]+\d{1,2}\s+([A-Za-z]+)\s+(\d{4})", raw)
    if range_match:
        try:
            d, m, y = range_match.groups()
            return datetime.strptime(f"{d} {m} {y}", "%d %b %Y").strftime("%Y-%m-%d")
        except ValueError:
            pass

    # Just year + month
    m = re.search(r"([A-Za-z]{3,9})\s+(\d{4})", raw)
    if m:
        mon_str, year = m.groups()
        mon = MONTH_ABBR.get(mon_str.lower())
        if mon:
            return f"{year}-{mon:02d}-01"

    # Just a year
    m = re.search(r"\b(20\d{2})\b", raw)
    if m:
        return f"{m.group(1)}-01-01"

    return ""


def month_label(iso: str) -> str:
    if len(iso) >= 7:
        try:
            return datetime.strptime(iso[:7], "%Y-%m").strftime("%B %Y")
        except ValueError:
            pass
    return "Unknown"


def detect_columns(header_row: list[str]) -> dict[str, int]:
    """Map field names to column indices from a header row."""
    mapping = {}
    keywords = {
        "name": ["tournament", "event", "name", "title", "championship"],
        "date": ["date", "dates", "when", "schedule"],
        "location": ["location", "venue", "city", "place", "where"],
        "category": ["category", "type", "class", "rating", "open", "age"],
        "organizer": ["organizer", "organised", "contact", "arbiter", "td"],
    }
    for i, cell in enumerate(header_row):
        lower = cell.lower()
        for field, keys in keywords.items():
            if field not in mapping and any(k in lower for k in keys):
                mapping[field] = i
    return mapping


def get_month(tour_date: str) -> str:
    end_date_part = tour_date.split("-")[-1]  # "13th April 2026"

    # 2. Strip out the 'th', 'st', 'nd', or 'rd' from the day
    clean_date_str = re.sub(r"(\d+)(st|nd|rd|th)", r"\1", end_date_part)  # "13 April 2026"

    # 3. Parse and format using datetime
    date_obj = datetime.strptime(clean_date_str, "%d %B %Y")
    if date_obj < datetime.now().replace(day=1):
        return "Past Tournament"
    formatted_date = date_obj.strftime("%b %Y")

    return formatted_date  # Output: Apr 2026


def scrape() -> list[dict]:
    req = urllib.request.Request(
        URL,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0 Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        html = resp.read().decode("utf-8", errors="replace")

    soup = BeautifulSoup(html, "html.parser")
    sections = soup.select("article .elementor-section")

    tournaments = []
    for section in sections[1:]:
        paragraphs = [p.get_text(" ", True) for p in section.find_all("p")]

        tour_type = ""
        if paragraphs[1].startswith("("):
            tour_type = paragraphs.pop(1)

        record = {
            "name": paragraphs[0],
            "category": tour_type,
            "location": paragraphs[1].lstrip("Chess Tournament in "),
            "date": paragraphs[2].replace(" To ", "-"),
            "prize_fund": paragraphs[3],
            "venue": paragraphs[4].replace("Venue :", "").strip(),
            "download_url": soup.find("a", class_="elementor-button")["href"],
        }
        record["month"] = get_month(record["date"])
        tournaments.append(record)

    tournaments.reverse()
    return tournaments


def main():
    print(f"Fetching {URL} ...")
    try:
        tournaments = scrape()
    except Exception as exc:
        print(f"ERROR: {exc}")
        raise
        tournaments = []

    out = {
        "updated": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source": URL,
        "count": len(tournaments),
        "tournaments": tournaments,
    }

    Path("data").mkdir(exist_ok=True)
    Path("data/chess.json").write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"✓ Saved {len(tournaments)} tournaments → data/chess.json")


if __name__ == "__main__":
    main()
