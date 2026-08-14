import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

DATA_DIR = Path("data")


def formatted_now() -> str:
    india_tz = timezone(timedelta(hours=5, minutes=30))
    return datetime.now(india_tz).strftime("%d %b %Y %H:%M IST")


def save_as_json(filename: str, data: dict):
    DATA_DIR.mkdir(exist_ok=True)
    file = Path("data") / filename
    file.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
