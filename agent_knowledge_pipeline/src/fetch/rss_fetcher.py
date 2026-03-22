import json
from pathlib import Path
from datetime import datetime, timezone

import feedparser


def fetch_rss(url: str, source_name: str) -> list[dict]:
    feed = feedparser.parse(url)
    items: list[dict] = []
    for e in feed.entries:
        items.append(
            {
                "source": source_name,
                "title": e.get("title", "").strip(),
                "link": e.get("link", "").strip(),
                "summary": e.get("summary", "").strip(),
                "published": e.get("published", ""),
                "fetched_at": datetime.now(timezone.utc).isoformat(),
            }
        )
    return items


def save_raw(items: list[dict], out_file: Path) -> None:
    out_file.parent.mkdir(parents=True, exist_ok=True)
    out_file.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")
