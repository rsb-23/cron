#!/usr/bin/env python3
"""
Weekly scraper for Chhattisgarh chess tournaments.
Source: https://chessevents.co.in/chhattisgarh-chess-tournament/
Output: data/chess.json
Run via: python scripts/fetch_chess.py
"""

import re
import urllib.request
from datetime import datetime

from bs4 import BeautifulSoup
from utils import formatted_now, save_as_json

URL = "https://chessevents.co.in/chhattisgarh-chess-tournament/"


def get_month(tour_date: str) -> str:
    end_date_part = tour_date.rsplit("-", maxsplit=1)[-1]  # "13th April 2026"

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
        paragraphs: list[str] = [p.get_text(" ", True) for p in section.find_all("p")]

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

    out = {"updated": formatted_now(), "source": URL, "count": len(tournaments), "tournaments": tournaments}
    save_as_json("chess.json", data=out)

    print(f"✓ Saved {len(tournaments)} tournaments → data/chess.json")


if __name__ == "__main__":
    main()
