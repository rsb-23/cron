import json
from datetime import datetime, timezone
from pathlib import Path

DATA_DIR = Path("data")


def formatted_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def save_as_json(filename: str, data: dict):
    DATA_DIR.mkdir(exist_ok=True)
    file = Path("data") / filename
    file.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
